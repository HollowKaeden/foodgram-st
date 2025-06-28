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

        count = 0
        for ingredient in data:
            name, unit = ingredient.values()
            _, created = Ingredient.objects.get_or_create(
                name=name, measurement_unit=unit
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Импортировано {count} '
                                             f'ингредиентов'))
