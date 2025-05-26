from django.urls import path
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated
from .views import AvatarViewSet


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


urlpatterns = [
    path('', user_list, name='user-list'),
    path('<int:id>/', user_detail, name='user-detail'),
    path('me/', user_me, name='user-me'),
    path('me/avatar',
         AvatarViewSet.as_view({'put': 'avatar',
                                'delete': 'avatar'}),
         name='avatar'),
    path('set_password/', set_password, name='user-set-password'),
]
