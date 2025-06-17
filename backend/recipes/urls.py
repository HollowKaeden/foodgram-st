from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RecipeViewSet, IngredientViewSet
from .views import short_recipe_view

router = SimpleRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('s/<int:recipe_id>/', short_recipe_view, name='short-link'),
]
