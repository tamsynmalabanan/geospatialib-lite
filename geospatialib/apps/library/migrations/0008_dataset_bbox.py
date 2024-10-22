# Generated by Django 5.1.2 on 2024-10-22 13:03

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_alter_dataset_added_by_alter_url_added_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='bbox',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Bounding box'),
        ),
    ]
