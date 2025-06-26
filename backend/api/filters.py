import django_filters
from django_filters import rest_framework as filters
from recipes.models import Recipe, Ingredient


class RecipeFilter(django_filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(method='filter_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_shopping_cart')

    def filter_favorited(self, recipes, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none() if value else recipes
        if int(value):
            return recipes.filter(favorites__user=user)
        return recipes

    def filter_shopping_cart(self, recipes, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none() if value else recipes
        if int(value):
            return recipes.filter(shopping_carts__user=user)
        return recipes

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
