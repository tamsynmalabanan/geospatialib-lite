# Generated by Django 5.1.2 on 2024-10-22 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_rename_join_date_user_joined_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='loggedin_on',
            field=models.DateTimeField(null=True, verbose_name='Join date'),
        ),
    ]