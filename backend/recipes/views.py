from django.shortcuts import redirect
from django.http import Http404
from recipes.models import Recipe


def short_recipe_view(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise Http404(f'Рецепт с id {recipe_id} не найден')
    return redirect(f'/recipes/{recipe_id}/')
