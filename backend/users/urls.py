from django.urls import path
from rest_framework.permissions import IsAuthenticated
from .views import UserViewSet


user_list = UserViewSet.as_view(
    {
        'get': 'list',
        'post': 'create'
    }
)

user_detail = UserViewSet.as_view(
    {
        'get': 'retrieve'
    }
)

user_me = UserViewSet.as_view(
    {
        'get': 'me',
    },
    permission_classes=[IsAuthenticated]
)

set_password = UserViewSet.as_view(
    {
        'post': 'set_password'
    }
)

avatar = UserViewSet.as_view(
    {
        'put': 'avatar',
        'delete': 'avatar'
    },
    permission_classes=[IsAuthenticated]
)


urlpatterns = [
    path('', user_list, name='user-list'),
    path('<int:id>/', user_detail, name='user-detail'),
    path('me/', user_me, name='user-me'),
    path('me/avatar', avatar, name='avatar'),
    path('set_password/', set_password, name='user-set-password'),
]
