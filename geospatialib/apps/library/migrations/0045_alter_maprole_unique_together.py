# Generated by Django 5.1.2 on 2024-11-24 08:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0044_alter_maprole_role'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='maprole',
            unique_together={('map', 'user')},
        ),
    ]
