from django.contrib import admin
from django.urls import path, include
from .views import short_recipe_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:code>/', short_recipe_view, name='short-link')
]
