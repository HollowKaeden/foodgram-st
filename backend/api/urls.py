from django.urls import path, include
from rest_framework.routers import SimpleRouter
from api.views import RecipeViewSet, IngredientViewSet
from api.views import UserViewSet
from rest_framework.permissions import IsAuthenticated


# Основной роутер
router = SimpleRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


# Маршруты пользователей
user_list = UserViewSet.as_view({'get': 'list', 'post': 'create'})
user_detail = UserViewSet.as_view({'get': 'retrieve'})
user_me = UserViewSet.as_view(
    {
        'get': 'me',
    },
    permission_classes=[IsAuthenticated]
)
set_password = UserViewSet.as_view({'post': 'set_password'})
avatar = UserViewSet.as_view(
    {
        'put': 'avatar',
        'delete': 'avatar'
    },
    permission_classes=[IsAuthenticated]
)
subscriptions = UserViewSet.as_view(
    {
        'get': 'subscriptions'
    },
    permission_classes=[IsAuthenticated]
)
subscribe = UserViewSet.as_view(
    {
        'post': 'subscribe',
        'delete': 'delete_subscription'
    },
    permission_classes=[IsAuthenticated]
)


users_urlpatterns = [
    path('', user_list, name='user-list'),
    path('<int:id>/', user_detail, name='user-detail'),
    path('me/', user_me, name='user-me'),
    path('me/avatar/', avatar, name='avatar'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('<int:id>/subscribe/', subscribe, name='subscribe'),
    path('set_password/', set_password, name='user-set-password'),
]


urlpatterns = [
    path('users/', include(users_urlpatterns)),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
