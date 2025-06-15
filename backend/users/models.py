from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy


class MyUser(AbstractUser):
    email = models.EmailField(gettext_lazy('email address'),
                              blank=False,
                              unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=False)
    last_name = models.CharField('Фамилия', max_length=150, blank=False)
    avatar = models.ImageField(
        "Аватар", upload_to="users/",
        blank=True, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
