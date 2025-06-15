from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid
import base64
from django.core.files.base import ContentFile
from djoser.views import UserViewSet as DjoserUserViewSet


class UserViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            avatar_b64 = request.data.get('avatar')
            if not avatar_b64:
                return Response({'avatar': ['Обязательное поле']},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                format, imgstr = avatar_b64.split(';base64,')
                ext = format.split('/')[-1]
                name = f'{uuid.uuid4()}.{ext}'
                data = ContentFile(base64.b64decode(imgstr), name=name)

                user.avatar.save(data.name, data, save=True)
                return Response({'avatar':
                                 request.build_absolute_uri(user.avatar.url)})
            except Exception:
                return Response({'error': 'Неправильные данные'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
