import django_filters
from django_filters import rest_framework as filters
from recipes.models import Recipe, Ingredient
from django.contrib.admin import SimpleListFilter


# Фильтры для API


class RecipeFilter(django_filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(method='filter_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_shopping_cart')

    def filter_favorited(self, recipes, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none() if value else recipes
        if int(value):
            return recipes.filter(favorite__user=user)
        return recipes

    def filter_shopping_cart(self, recipes, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none() if value else recipes
        if int(value):
            return recipes.filter(shoppingcart__user=user)
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


# Фильтры для админ-панели

class CookingTimeFilter(SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time_range'

    def lookups(self, request, model_admin):
        recipes = Recipe.objects.all().values_list('cooking_time', flat=True)
        if not recipes:
            return list()

        sorted_times = sorted(recipes)
        total = len(sorted_times)

        shortest_border = sorted_times[total // 3]
        longest_border = sorted_times[(2 * total) // 3]

        self.shortest_border = shortest_border
        self.longest_border = longest_border

        fast = Recipe.objects.filter(cooking_time__lt=shortest_border).count()
        medium = Recipe.objects.filter(cooking_time__gte=shortest_border,
                                       cooking_time__lt=longest_border).count()
        long = Recipe.objects.filter(cooking_time__gte=longest_border).count()

        return [
            ('<', f'Быстрее {shortest_border} мин ({fast})'),
            ('<>', f'Быстрее {longest_border} мин ({medium})'),
            ('>', f'Долго ({long})')
        ]

    def queryset(self, request, recipes_queryset):
        if self.value():
            if self.value() == '<':
                return recipes_queryset.filter(
                    cooking_time__lt=self.shortest_border
                )
            elif self.value() == '<>':
                return recipes_queryset.filter(
                    cooking_time__gte=self.shortest_border,
                    cooking_time__lt=self.longest_border
                )
            elif self.value() == '>':
                return recipes_queryset.filter(
                    cooking_time__gte=self.longest_border
                )
        return recipes_queryset


class IsUsedInRecipesFilter(SimpleListFilter):
    title = 'Есть в рецептах'
    parameter_name = 'is_used_in_recipes'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, ingredients_queryset):
        if self.value() == 'yes':
            return ingredients_queryset.filter(recipes_count__gt=0)
        if self.value() == 'no':
            return ingredients_queryset.filter(recipes_count=0)
        return ingredients_queryset
