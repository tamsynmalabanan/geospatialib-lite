# Generated by Django 5.1.2 on 2024-10-20 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='First name'),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Last name'),
        ),
    ]
