# Generated by Django 5.1.2 on 2024-10-21 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_alter_dataset_format'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Dataset',
        ),
        migrations.DeleteModel(
            name='URL',
        ),
    ]