# Generated by Django 5.1.2 on 2024-10-18 15:18

import apps.main.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_user_is_active_user_is_staff_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.SlugField(unique=True, validators=[apps.main.validators.validate_username], verbose_name='Username'),
        ),
    ]
