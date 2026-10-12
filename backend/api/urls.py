from django.urls import path, include
from rest_framework.routers import SimpleRouter
from api.views import RecipeViewSet, IngredientViewSet
from api.views import UserViewSet, ThrottledTokenCreateView


router = SimpleRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    # Логин с троттлингом; стоит раньше djoser, поэтому перекрывает его login
    path('auth/token/login/', ThrottledTokenCreateView.as_view(),
         name='login'),
    path('auth/', include('djoser.urls.authtoken')),
]
