# Generated by Django 5.1.2 on 2024-12-03 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0010_remove_maplog_user_map_added_by_map_added_on_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='maplog',
            name='action',
            field=models.CharField(blank=True, choices=[('set', 'Set'), ('removed', 'Removed'), ('changed', 'Changed'), ('added', 'Added')], max_length=8, null=True, verbose_name='Action'),
        ),
    ]
