# Generated by Django 5.1.2 on 2024-10-21 16:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0004_delete_dataset_delete_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True, verbose_name='Added on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('path', models.URLField(max_length=256, unique=True, verbose_name='URL')),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)ss_added', to=settings.AUTH_USER_MODEL, verbose_name='Added by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)ss_updated', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True, verbose_name='Added on')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('format', models.CharField(choices=[('wms', 'OGC Web Map Service'), ('xyz', 'XYZ Tiles')], max_length=16, verbose_name='Format')),
                ('name', models.CharField(max_length=256, verbose_name='Layer')),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)ss_added', to=settings.AUTH_USER_MODEL, verbose_name='Added by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='%(class)ss_updated', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.url', verbose_name='URL')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
