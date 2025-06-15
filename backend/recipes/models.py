from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=256
    )
    image = models.ImageField(
        'Изображение', upload_to='recipes/images/'
    )
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveIntegerField('Время приготовления',
                                               validators=(
                                                   MinValueValidator(1),))
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return (f'{self.name} - '
                f'{self.author.first_name} {self.author.last_name}')


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=64, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=16)

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        'Количество', validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = 'связь рецепта с ингредиентом'
        verbose_name_plural = 'Связи рецептов и ингредиентов'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}: {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'любимое'
        verbose_name_plural = 'Любимые'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shoppingcart'
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.recipe}'
