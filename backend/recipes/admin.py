from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db.models import Count
from recipes.models import (Recipe, Ingredient, RecipeIngredient,
                            Favorite, ShoppingCart)
from api.filters import CookingTimeFilter, IsUsedInRecipesFilter


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorites_count',)
    search_fields = ('name', 'author__email',
                     'author__first_name', 'author__last_name')
    list_display = ('id', 'name', 'cooking_time', 'author',
                    'favorites_count', 'ingredients_list', 'image_preview')
    list_filter = ('author', CookingTimeFilter)

    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        qs = qs.annotate(favorites_count=Count('favorite'))
        return qs

    @admin.display(description='В избранном')
    def favorites_count(self, recipe):
        return recipe.favorites_count

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_list(self, recipe):
        return '<br>'.join(f'{ri.ingredient.name} - '
                           f'{ri.amount} {ri.ingredient.measurement_unit}'
                           for ri in recipe.recipe_ingredients.all())

    @admin.display(description='Фото')
    @mark_safe
    def image_preview(self, recipe):
        if recipe.image:
            image_url = self.request.build_absolute_uri(recipe.image.url)
            return f'<img src="{image_url}" width="100" height="100"/>'
        return '-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', IsUsedInRecipesFilter)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(recipes_count=Count('recipes'))
        return qs

    @admin.display(description='Количество рецептов')
    def recipes_count(self, ingredient):
        return ingredient.recipes_count


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
