from django.urls import path, include
from rest_framework.routers import SimpleRouter
from api.views import RecipeViewSet, IngredientViewSet


router = SimpleRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('users/', include('users.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
