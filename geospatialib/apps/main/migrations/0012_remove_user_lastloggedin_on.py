# Generated by Django 5.1.2 on 2024-10-22 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_user_lastloggedin_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='lastloggedin_on',
        ),
    ]
