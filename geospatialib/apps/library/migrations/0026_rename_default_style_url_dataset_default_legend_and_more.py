# Generated by Django 5.1.2 on 2024-11-10 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0025_dataset_default_style_name_dataset_default_style_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='default_style_url',
            new_name='default_legend',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='default_style_name',
            new_name='default_style',
        ),
    ]