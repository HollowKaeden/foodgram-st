import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from recipes.models import Recipe


# Этот класс не лишний, используется в recipes и users и добавлен
# для избежания цикличного импорта
# TODO При слиянии приложений можно его добавить в recipes
class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
