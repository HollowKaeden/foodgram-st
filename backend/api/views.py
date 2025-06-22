from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        elif self.action == 'favorite':
            return ShortRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        return serializer.save()

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
        self._add_user_recipe_relation(Favorite, request.user, pk,
                                       f'Рецепт с id={pk} уже в избранном')

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        self._delete_user_recipe_relation(Favorite, request.user, pk)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def add_to_cart(self, request, pk=None):
        self._add_user_recipe_relation(ShoppingCart, request.user, pk,
                                       f'Рецепт с id={pk} уже в корзине')

    @add_to_cart.mapping.delete
    def delete_from_cart(self, request, pk=None):
        self._delete_user_recipe_relation(ShoppingCart, request.user, pk)

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
