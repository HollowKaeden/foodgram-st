from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Recipe
from .serializers import RecipeSerializer, RecipeCreateUpdateSerializer
from .permissions import IsAuthorOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_create(serializer)
        output_serializer = RecipeSerializer(recipe,
                                             context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(output_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        output_serializer = RecipeSerializer(recipe,
                                             context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)
