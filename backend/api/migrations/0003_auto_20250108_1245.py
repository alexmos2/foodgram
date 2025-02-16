# Generated by Django 3.2.3 on 2025-01-08 09:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientreceipt',
            name='amount',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Минимальное количество: 1'), django.core.validators.MaxValueValidator(10000, 'Максимальное количество: 10000')], verbose_name='Число'),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Минимальное время готовки: 1 минут'), django.core.validators.MaxValueValidator(10000, 'Максимальное время готовки: 10000 минут')], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='short_link',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
