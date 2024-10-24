# Generated by Django 5.1.2 on 2024-10-23 11:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0011_alter_dataset_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='library.url', verbose_name='URL'),
        ),
    ]
