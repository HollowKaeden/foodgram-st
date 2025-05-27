from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import RecipeViewSet

router = SimpleRouter()
router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('', include(router.urls))
]
