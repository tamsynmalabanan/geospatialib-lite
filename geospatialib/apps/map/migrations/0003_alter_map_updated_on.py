# Generated by Django 5.1.2 on 2024-11-30 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_alter_maprole_options_alter_map_updated_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='updated_on',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Updated on'),
        ),
    ]
