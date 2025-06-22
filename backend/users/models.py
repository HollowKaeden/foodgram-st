from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\z',
    message='Имя пользователя может содержать '
            'только буквы, цифры и символы @/./+/-/_'
)


class CustomUser(AbstractUser):
    username = models.CharField('Имя пользователя', max_length=150,
                                unique=True, validators=(username_validator,))
    email = models.EmailField('Электронная почта', max_length=254,
                              blank=False, unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=False)
    last_name = models.CharField('Фамилия', max_length=150, blank=False)
    avatar = models.ImageField(
        "Аватар", upload_to="users/",
        blank=True, null=True,
        default='users/default_avatar.jpg'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = 'users/default_avatar.jpg'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        ordering = ('subscriber', 'author')
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'{self.subscriber.first_name} {self.subscriber.last_name} - '
                f'{self.author.first_name} {self.author.last_name}')
