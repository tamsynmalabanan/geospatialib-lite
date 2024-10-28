# Generated by Django 5.1.2 on 2024-10-28 06:37

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0022_alter_dataset_unique_together_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(choices=[('wms', 'OGC Web Map Service'), ('xyz', 'XYZ Tiles')], max_length=16, verbose_name='Format')),
                ('name', models.CharField(max_length=255, verbose_name='Layer')),
                ('extra_data', models.JSONField(blank=True, null=True, verbose_name='Data')),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=255, verbose_name='Tag')),
            ],
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=255, unique=True, verbose_name='URL')),
            ],
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('added_on', models.DateTimeField(auto_now_add=True, verbose_name='Added on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('type', models.CharField(choices=[('dataset', 'dataset'), ('map', 'map')], default='dataset', editable=False, max_length=8, verbose_name='Type')),
                ('label', models.CharField(blank=True, max_length=255, null=True, verbose_name='label')),
                ('bbox', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Bounding box')),
                ('abstract', models.TextField(blank=True, null=True, verbose_name='Abstract')),
                ('added_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)ss_added', to=settings.AUTH_USER_MODEL, verbose_name='Added by')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)ss_updated', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('dataset', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='library.dataset', verbose_name='Dataset')),
                ('map', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='library.map', verbose_name='Map')),
                ('tags', models.ManyToManyField(blank=True, to='library.tag', verbose_name='Tags')),
            ],
        ),
        migrations.AddField(
            model_name='dataset',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='library.url', verbose_name='URL'),
        ),
        migrations.AlterUniqueTogether(
            name='dataset',
            unique_together={('url', 'format', 'name')},
        ),
    ]