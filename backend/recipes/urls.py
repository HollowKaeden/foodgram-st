from django.urls import path
from .views import short_recipe_view


urlpatterns = [
    path('s/<int:recipe_id>/', short_recipe_view, name='short-link'),
]
