from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from recipes.models import Recipe


def short_recipe_view(request, code):
    try:
        recipe_id = int(code, 16)
    except ValueError:
        return JsonResponse({'errors': 'Неправильный формат кода'}, status=400)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return redirect(f'/api/recipes/{recipe.id}/')
