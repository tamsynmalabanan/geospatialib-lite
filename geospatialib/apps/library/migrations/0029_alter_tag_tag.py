# Generated by Django 5.1.2 on 2024-11-18 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0028_alter_dataset_format'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tag',
            field=models.CharField(max_length=255, unique=True, verbose_name='Tag'),
        ),
    ]