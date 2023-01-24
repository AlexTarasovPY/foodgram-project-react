# Generated by Django 4.1.3 on 2023-01-24 10:43

from django.db import migrations

INITIAL_TAGS = [
    {'color': '#90EE90', 'name': 'Завтрак', 'slug': 'breakfasttt'},
    {'color': '#ADD8E6', 'name': 'Обед', 'slug': 'lunchhh'},
    {'color': '#FF7F50', 'name': 'Ужин', 'slug': 'dinnerrr'},
]


def add_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    for tag in INITIAL_TAGS:
        new_tag = Tag(**tag)
        new_tag.save()


def delete_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    for tag in INITIAL_TAGS:
        Tag.objects.get(slug=tag['slug']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_tags,
            delete_tags
        )
    ]
