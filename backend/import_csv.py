import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()

from api.models import Ingredient, Tag


csv_file_path = 'ingredients.csv'

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        Ingredient.objects.get_or_create(
            name=row['name'], measurement_unit=row['measurement_unit']
        )
        print(f"Добавлен ингредиент: {row['name']}")

csv_file_path = 'tags.csv'

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        Tag.objects.get_or_create(name=row['name'], slug=row['slug'])
        print(f"Добавлен тег: {row['name']}")
