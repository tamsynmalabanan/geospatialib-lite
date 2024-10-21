# Generated by Django 5.1.2 on 2024-10-18 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_alter_dataset_format_alter_dataset_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='format',
            field=models.CharField(choices=[('ogc-wms', 'OGC Web Map Service'), ('xyz-tiles', 'XYZ Tiles')], max_length=16, verbose_name='Format'),
        ),
    ]