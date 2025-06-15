from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import uuid
import base64
from django.core.files.base import ContentFile
from djoser.views import UserViewSet as DjoserUserViewSet
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Subscription
from .serializers import SubscriptionsSerializer


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            avatar_b64 = request.data.get('avatar')
            if not avatar_b64:
                return Response({'avatar': ['Обязательное поле']},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                format, imgstr = avatar_b64.split(';base64,')
                ext = format.split('/')[-1]
                name = f'{uuid.uuid4()}.{ext}'
                data = ContentFile(base64.b64decode(imgstr), name=name)

                user.avatar.save(data.name, data, save=True)
                return Response({'avatar':
                                 request.build_absolute_uri(user.avatar.url)})
            except Exception:
                return Response({'error': 'Неправильные данные'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(subscriber=request.user)
        authors = User.objects.filter(id__in=subscriptions
                                      .values_list('author_id', flat=True))

        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except (TypeError, ValueError):
            recipes_limit = None

        context = self.get_serializer_context()
        context['recipes_limit'] = recipes_limit

        page = self.paginate_queryset(authors)
        serializer = SubscriptionsSerializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(subscriber=user,
                                       author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(subscriber=user, author=author)
        serializer = SubscriptionsSerializer(author,
                                             context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(subscriber=user,
                                                   author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
