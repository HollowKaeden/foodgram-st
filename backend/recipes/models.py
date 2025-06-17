from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=256
    )
    image = models.ImageField(
        'Изображение', upload_to='recipes/images/'
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name='Продукты'
    )
    cooking_time = models.PositiveIntegerField('Время приготовления',
                                               validators=(
                                                   MinValueValidator(1),))
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return (f'{self.name} - '
                f'{self.author.first_name} {self.author.last_name}')


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        ordering = ('name',)
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_unit_relation'
            )
        )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    amount = models.PositiveIntegerField(
        'Количество', validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = 'связь рецепта с продуктом'
        verbose_name_plural = 'Связи рецептов и продуктов'
        default_related_name = 'recipe_ingredients'
        ordering = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}: {self.amount}'


class UserRecipeLink(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_relation'
            )
        )

    def __str__(self):
        return f'{self.user} - {self.recipe.name}'


class Favorite(UserRecipeLink):
    class Meta:
        verbose_name = 'любимое'
        verbose_name_plural = 'Любимые'
        default_related_name = 'favorites'


class ShoppingCart(UserRecipeLink):
    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзина'
        default_related_name = 'shopping_carts'
