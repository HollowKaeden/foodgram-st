from django.contrib import admin
from .models import (Recipe, Ingredient, RecipeIngredient,
                     Favorite, ShoppingCart)


admin.site.register((Recipe, Ingredient, RecipeIngredient,
                     Favorite, ShoppingCart))
