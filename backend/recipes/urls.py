from django.urls import path
from recipes.views import short_recipe_view


urlpatterns = [
    path('s/<int:recipe_id>/', short_recipe_view, name='short-link'),
]
