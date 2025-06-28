import json
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из файла ingredients.json'

    def handle(self, *args, **options):
        try:
            with open('ingredients.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise CommandError('Файл ingredients.json не найден')

        new_ingredients = [Ingredient(**ingredient) for ingredient in data]

        before = Ingredient.objects.count()
        Ingredient.objects.bulk_create(new_ingredients, ignore_conflicts=True)
        after = Ingredient.objects.count()

        self.stdout.write(self.style.SUCCESS(f'Импортировано {after - before} '
                                             f'ингредиентов'))
