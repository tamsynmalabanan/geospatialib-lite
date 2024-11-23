# Generated by Django 5.1.2 on 2024-11-23 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0039_alter_maprole_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='privacy',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private')], default='public', max_length=8, verbose_name='Privacy'),
        ),
    ]
