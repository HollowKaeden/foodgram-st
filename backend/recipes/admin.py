from django.contrib import admin
from .models import (Recipe, Ingredient, RecipeIngredient,
                     Favorite, ShoppingCart)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author__email',
                     'author__first_name', 'author__last_name')


admin.site.register((Ingredient, RecipeIngredient,
                     Favorite, ShoppingCart))
