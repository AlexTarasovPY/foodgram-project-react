# Generated by Django 4.1.3 on 2023-01-24 11:05

from django.db import migrations
import json

with open('data/ingredients.json', 'r', encoding='utf-8') as json_file:
    INGREDIENTS = json.load(json_file)


def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    for ingredient in INGREDIENTS:
        new_ingredient = Ingredient(**ingredient)
        new_ingredient.save()


def delete_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    for ingredient in INGREDIENTS:
        Ingredient.objects.get(name=ingredient['name']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_add_tags'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
            delete_ingredients
        )

    ]
