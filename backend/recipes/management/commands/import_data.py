import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Наполнение БД из файлов CSV'

    def handle(self, *args, **options):
        with open(
                '../data/ingredients.csv',
                'r',
                encoding='UTF-8'
        ) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
