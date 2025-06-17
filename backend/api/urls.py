from django.urls import path, include
from djoser.views import TokenCreateView, TokenDestroyView


urlpatterns = [
    path('users/', include('users.urls')),
    path('', include('recipes.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
