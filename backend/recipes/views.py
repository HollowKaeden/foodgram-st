from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from .models import Recipe, Ingredient, Favorite, ShoppingCart
from .serializers import (RecipeSerializer,
                          RecipeCreateUpdateSerializer,
                          IngredientSerializer)
from api.serializers import ShortRecipeSerializer
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter, IngredientFilter


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_create(serializer)
        output_serializer = RecipeSerializer(recipe,
                                             context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(output_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        output_serializer = RecipeSerializer(recipe,
                                             context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'errors': 'Рецепт не был в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        hex_id = format(recipe.id, 'x')
        short_link = request.build_absolute_uri(
            reverse('short-link', kwargs={'code': hex_id})
        )
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_cart(self, request):
        user = request.user
        recipe_ids = (ShoppingCart.objects.filter(user=user)
                      .values_list('recipe', flat=True))
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

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def add_to_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': 'Рецепт уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_to_cart.mapping.delete
    def delete_from_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not cart_item.exists():
            return Response(
                {'errors': 'Рецепт не был в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None
