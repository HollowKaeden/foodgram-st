from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RecipeViewSet, IngredientViewSet

router = SimpleRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls))
]
