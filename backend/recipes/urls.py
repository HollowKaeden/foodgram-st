from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RecipeViewSet, IngredientViewSet

router = SimpleRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls))
]
