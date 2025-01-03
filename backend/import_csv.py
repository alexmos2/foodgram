import os
import django
import csv


def import_ingredients():
    csv_file_path = 'ingredients.csv'
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            Ingredient.objects.get_or_create(
                name=row['name'], measurement_unit=row['measurement_unit']
            )
            print(f"Добавлен ингредиент: {row['name']}")


def import_tags():
    csv_file_path = 'tags.csv'
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            Tag.objects.get_or_create(name=row['name'], slug=row['slug'])
            print(f"Добавлен тег: {row['name']}")


if __name__ == "__main__":
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
    django.setup()
    from api.models import Ingredient, Tag
    import_ingredients()
    import_tags()
