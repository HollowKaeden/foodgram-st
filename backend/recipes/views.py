from django.shortcuts import get_object_or_404, redirect
from recipes.models import Recipe


def short_recipe_view(request, recipe_id):
    # Http404, а не ValidationError из DRF: это обычная Django-вьюха,
    # исключение DRF здесь никто не обрабатывает, и получался 500.
    get_object_or_404(Recipe, id=recipe_id)
    return redirect(f'/recipes/{recipe_id}/')
