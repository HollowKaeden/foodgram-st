from django.conf import settings
from rest_framework.exceptions import ValidationError


def validate_image_size(file):
    """Не даёт загрузить картинку больше MAX_IMAGE_SIZE_MB (0 = без лимита)."""
    limit_mb = settings.MAX_IMAGE_SIZE_MB
    if limit_mb and file.size > limit_mb * 1024 * 1024:
        raise ValidationError(
            f'Картинка слишком большая, максимум {limit_mb:g} МБ')
