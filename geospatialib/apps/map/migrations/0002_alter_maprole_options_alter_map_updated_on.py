# Generated by Django 5.1.2 on 2024-11-28 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maprole',
            options={'ordering': ['-role']},
        ),
        migrations.AlterField(
            model_name='map',
            name='updated_on',
            field=models.DateTimeField(verbose_name='Updated on'),
        ),
    ]