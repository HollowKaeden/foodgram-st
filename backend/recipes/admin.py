from django.contrib import admin
from django.db.models import Count
from .models import (Recipe, Ingredient, RecipeIngredient,
                     Favorite, ShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorites_count',)
    search_fields = ('name', 'author__email',
                     'author__first_name', 'author__last_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(favorites_count=Count('favorite'))
        return qs

    def favorites_count(self, obj):
        return obj.favorites_count
    favorites_count.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register((RecipeIngredient, Favorite, ShoppingCart))
