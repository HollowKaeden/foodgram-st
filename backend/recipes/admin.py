from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.db.models import Count
from recipes.models import (CustomUser, Recipe, Ingredient, RecipeIngredient,
                            Favorite, ShoppingCart, Subscription)
from django.contrib.admin import SimpleListFilter


class CookingTimeFilter(SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time_range'

    def lookups(self, request, model_admin):
        times = Recipe.objects.all().values_list('cooking_time',
                                                 flat=True).distinct()
        if len(times) < 3:
            return list()

        sorted_times = sorted(times)
        total = len(sorted_times)

        self.shortest_border = sorted_times[total // 3]
        self.longest_border = sorted_times[(2 * total) // 3]

        fast = Recipe.objects.filter(cooking_time__lt=self.shortest_border)
        medium = Recipe.objects.filter(cooking_time__gte=self.shortest_border,
                                       cooking_time__lt=self.longest_border)
        long = Recipe.objects.filter(cooking_time__gte=self.longest_border)

        return [
            ('<', f'Быстрее {self.shortest_border} мин ({fast.count()})'),
            ('<>', f'Быстрее {self.longest_border} мин ({medium.count()})'),
            ('>', f'Долго ({long.count()})')
        ]

    def queryset(self, request, recipes_queryset):
        if self.value() == '<':
            return recipes_queryset.filter(
                cooking_time__lt=self.shortest_border
            )
        if self.value() == '<>':
            return recipes_queryset.filter(
                cooking_time__gte=self.shortest_border,
                cooking_time__lt=self.longest_border
            )
        if self.value() == '>':
            return recipes_queryset.filter(
                cooking_time__gte=self.longest_border
            )
        return recipes_queryset


class IsUsedInRecipesFilter(SimpleListFilter):
    title = 'Есть в рецептах'
    parameter_name = 'is_used_in_recipes'
    LOOKUP_CHOICES = (
        ('yes', 'Да'),
        ('no', 'Нет'),
    )

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, ingredients_queryset):
        if self.value() == 'yes':
            return ingredients_queryset.filter(recipes_count__gt=0)
        if self.value() == 'no':
            return ingredients_queryset.filter(recipes_count=0)
        return ingredients_queryset


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    search_fields = ('email', 'username')
    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'image_preview',
        'recipes_count',
        'subscriptions_count',
        'subscribers_count',
    )

    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        qs = qs.annotate(
            recipes_count=Count('recipes'),
            subscriptions_count=Count('subscriptions_from'),
            subscribers_count=Count('subscribers_to')
        )
        return qs

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def image_preview(self, user):
        if user.avatar:
            avatar_url = self.request.build_absolute_uri(user.avatar.url)
            return f'<img src="{avatar_url}" width="100" height="100"/>'
        return '-'

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, user):
        return user.recipes_count

    @admin.display(description='Кол-во подписок')
    def subscriptions_count(self, user):
        return user.subscriptions_count

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, user):
        return user.subscribers_count


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorites_count',)
    search_fields = ('name', 'author__email',
                     'author__first_name', 'author__last_name')
    list_display = ('id', 'name', 'cooking_time', 'author',
                    'favorites_count', 'ingredients_list', 'image_preview')
    list_filter = ('author', CookingTimeFilter)

    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        qs = qs.annotate(favorites_count=Count('favorites'))
        return qs

    @admin.display(description='В избранном')
    def favorites_count(self, recipe):
        return recipe.favorites_count

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_list(self, recipe):
        return '<br>'.join(f'{ri.ingredient.name} - '
                           f'{ri.amount} {ri.ingredient.measurement_unit}'
                           for ri in recipe.recipe_ingredients.all())

    @admin.display(description='Фото')
    @mark_safe
    def image_preview(self, recipe):
        if recipe.image:
            image_url = self.request.build_absolute_uri(recipe.image.url)
            return f'<img src="{image_url}" width="100" height="100"/>'
        return '-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', IsUsedInRecipesFilter)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(recipes_count=Count('recipes'))
        return qs

    @admin.display(description='Количество рецептов')
    def recipes_count(self, ingredient):
        return ingredient.recipes_count


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
