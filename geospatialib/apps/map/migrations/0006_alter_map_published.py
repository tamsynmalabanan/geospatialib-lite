# Generated by Django 5.1.2 on 2024-12-02 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0005_remove_map_updated_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='published',
            field=models.BooleanField(default=False, verbose_name='Publication status'),
        ),
    ]