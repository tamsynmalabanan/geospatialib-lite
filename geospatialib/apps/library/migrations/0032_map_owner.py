# Generated by Django 5.1.2 on 2024-11-21 10:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0031_map_focus_area'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='maps', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
    ]
