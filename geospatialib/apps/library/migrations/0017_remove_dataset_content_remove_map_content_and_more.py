# Generated by Django 5.1.2 on 2024-10-26 07:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0016_content_dataset_content_map'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='content',
        ),
        migrations.RemoveField(
            model_name='map',
            name='content',
        ),
        migrations.AddField(
            model_name='content',
            name='dataset',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='library.dataset', verbose_name='Dataset'),
        ),
        migrations.AddField(
            model_name='content',
            name='map',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='library.map', verbose_name='Map'),
        ),
    ]