from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Subscription
from drf_extra_fields.fields import Base64ImageField
from api.serializers import ShortRecipeSerializer


User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            return False
        return Subscription.objects.filter(subscriber=user,
                                           author=author).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )


class SubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:recipes_limit]

        serializer = ShortRecipeSerializer(recipes, many=True,
                                           context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            return min(recipes_limit, obj.recipes.count())
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )
