# Generated by Django 5.1.2 on 2024-10-22 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_rename_join_data_user_join_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='join_date',
            new_name='joined_on',
        ),
    ]
