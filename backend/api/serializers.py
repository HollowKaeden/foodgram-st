from rest_framework import serializers
from recipes.models import (Recipe, Ingredient, RecipeIngredient,
                            Favorite, ShoppingCart)
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from recipes.models import Subscription
from djoser.serializers import UserSerializer as DjoserUserSerializer


User = get_user_model()


# Сериализаторы для пользователей и подписок


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(DjoserUserSerializer):
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


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, author):
        recipes_limit = self.context.get('recipes_limit')

        recipes = author.recipes.all()
        if recipes_limit:
            recipes = recipes[:recipes_limit]

        serializer = ShortRecipeSerializer(recipes, many=True,
                                           context=self.context)
        return serializer.data

    def get_recipes_count(self, author):
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            return min(recipes_limit, author.recipes.count())
        return author.recipes.count()

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


# Сериализаторы для рецептов и ингредиентов


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = (serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(source='recipe_ingredients',
                                               many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        return (user and user.is_authenticated
                and Favorite.objects.filter(user=user, recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = fields


class IngredientAmountSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(min_value=1)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True, required=True)
    image = Base64ImageField(required=True, allow_null=False)
    cooking_time = serializers.IntegerField(min_value=1)

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            ) for item in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().create({**validated_data,
                                 'author': self.context['request'].user})
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        self.validate_ingredients(ingredients)
        instance = super().update(instance, validated_data)

        instance.recipe_ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Нужно указать хотя '
                                              'бы один ингредиент')

        ingredient_ids = [item['ingredient'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError('Ингредиенты не '
                                              'должны повторяться')

        return ingredients

    def validate_image(self, image):
        if image in ("", None):
            raise serializers.ValidationError('Изображение обязательно.')
        return image

    class Meta:
        model = Recipe
        fields = ('ingredients', 'image', 'name', 'text', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
