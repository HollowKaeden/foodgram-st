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
        blank=True, null=True,
        default='users/default_avatar.jpg'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = 'users/default_avatar.jpg'
        super().save(*args, **kwargs)


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

    def __str__(self):
        return (f'{self.subscriber.first_name} {self.subscriber.last_name} - '
                f'{self.author.first_name} {self.author.last_name}')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
