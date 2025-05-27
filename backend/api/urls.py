from django.urls import path, include
from djoser.views import TokenCreateView, TokenDestroyView


urlpatterns = [
    path('users/', include('users.urls')),
    path('', include('recipes.urls')),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout')
]
