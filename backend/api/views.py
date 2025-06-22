from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from recipes.models import Recipe, Ingredient, Favorite, ShoppingCart
from api.serializers import (RecipeSerializer,
                             RecipeCreateUpdateSerializer,
                             IngredientSerializer)
from api.serializers import ShortRecipeSerializer
from api.permissions import IsAuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
from djoser.views import UserViewSet as DjoserUserViewSet
import uuid
import base64
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from recipes.models import Subscription
from api.serializers import SubscriptionSerializer


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            return (IsAuthenticated(), IsAuthorOrReadOnly())
        return (IsAuthorOrReadOnly(),)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        elif self.action == 'favorite':
            return ShortRecipeSerializer
        return RecipeSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                {'errors': f'Рецепт с id={pk} не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        short_path = reverse('short-link', kwargs={'recipe_id': pk})
        short_link = request.build_absolute_uri(short_path)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    def _add_user_recipe_relation(self, model, user, recipe_pk, error_msg):
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response({'errors': error_msg},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe,
                                           context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_user_recipe_relation(self, model, user, recipe_pk):
        obj = get_object_or_404(model, user=user, recipe_id=recipe_pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._add_user_recipe_relation(Favorite, request.user, pk,
                                              f'Рецепт с id={pk} уже '
                                              f'в избранном')

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self._delete_user_recipe_relation(Favorite, request.user, pk)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def add_to_cart(self, request, pk=None):
        return self._add_user_recipe_relation(ShoppingCart, request.user, pk,
                                              f'Рецепт с id={pk} уже '
                                              f'в корзине')

    @add_to_cart.mapping.delete
    def delete_from_cart(self, request, pk=None):
        return self._delete_user_recipe_relation(ShoppingCart, request.user,
                                                 pk)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_cart(self, request):
        user = request.user
        recipe_ids = user.shopping_carts.values_list('recipe', flat=True)
        recipes = Recipe.objects.filter(id__in=recipe_ids)
        cart = dict()
        for recipe in recipes:
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient = recipe_ingredient.ingredient
                amount = recipe_ingredient.amount
                if ingredient.name in cart:
                    cart[ingredient.name][0] += amount
                else:
                    cart[ingredient.name] = [amount,
                                             ingredient.measurement_unit]
        return render(request, 'shopping_cart.html', {'cart': cart})


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


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
        serializer = SubscriptionSerializer(page, many=True, context=context)
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

        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except (TypeError, ValueError):
            recipes_limit = None

        context = self.get_serializer_context()
        context['recipes_limit'] = recipes_limit

        serializer = SubscriptionSerializer(author, context=context)
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
