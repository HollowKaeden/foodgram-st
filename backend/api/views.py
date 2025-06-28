from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Recipe, Ingredient, Favorite,
                            ShoppingCart, Subscription)
from api.serializers import (RecipeReadSerializer,
                             RecipeCreateUpdateSerializer,
                             ShortRecipeSerializer,
                             IngredientSerializer,
                             UserWithRecipesSerializer)
from api.permissions import IsAuthorOrReadOnly
from api.filters import RecipeFilter, IngredientFilter
import uuid
import base64


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
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise ValidationError(f'Рецепт с id={pk} не найден')

        short_path = reverse('short-link', kwargs={'recipe_id': pk})
        short_link = request.build_absolute_uri(short_path)
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    def _add_user_recipe_relation(self, model, user, recipe_pk):
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            place = 'избранном' if model is Favorite else 'корзине'
            return Response({'errors': f'Рецепт с id={recipe_pk} в {place}'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ShortRecipeSerializer(recipe,
                                           context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_user_recipe_relation(self, model, user, recipe_pk):
        get_object_or_404(model, user=user, recipe_id=recipe_pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._add_user_recipe_relation(Favorite, request.user, pk)

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
        return self._add_user_recipe_relation(ShoppingCart, request.user, pk)

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

        page = self.paginate_queryset(authors)
        context = self.get_serializer_context()
        serializer = UserWithRecipesSerializer(page, many=True,
                                               context=context)
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

        subscription, created = (Subscription.objects
                                 .get_or_create(subscriber=user,
                                                author=author))
        if not created:
            return Response(
                {'errors':
                 f'Вы уже подписаны на пользователя {author.username}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        context = self.get_serializer_context()
        serializer = UserWithRecipesSerializer(author, context=context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, id=None):
        get_object_or_404(
            Subscription,
            subscriber=request.user,
            author_id=id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
