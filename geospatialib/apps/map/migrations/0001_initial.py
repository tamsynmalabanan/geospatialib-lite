# Generated by Django 5.1.2 on 2024-11-27 06:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_since', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Owner since')),
                ('privacy', models.CharField(choices=[('default', 'Default'), ('public', 'Public'), ('private', 'Private')], default='default', max_length=8, verbose_name='Privacy')),
                ('privacy_changed', models.DateTimeField(blank=True, null=True, verbose_name='Date privacy changed')),
                ('published', models.BooleanField(default=False, verbose_name='Published')),
                ('published_on', models.DateTimeField(blank=True, null=True, verbose_name='Date published')),
                ('published_off', models.DateTimeField(blank=True, null=True, verbose_name='Date unpublished')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('focus_area', models.CharField(blank=True, max_length=255, null=True, verbose_name='Focus area')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maps', to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
        ),
        migrations.CreateModel(
            name='MapLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Added on')),
                ('field', models.CharField(max_length=50, verbose_name='Field')),
                ('value', models.TextField(verbose_name='Value')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='map.map', verbose_name='Map')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='MapReference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, verbose_name='Label')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='references', to='map.map', verbose_name='Map')),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.url', verbose_name='URL')),
            ],
        ),
        migrations.CreateModel(
            name='MapRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Added on')),
                ('updated_on', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated on')),
                ('role', models.SmallIntegerField(choices=[(3, 'Admin'), (2, 'Editor'), (1, 'Reviewer')], default=2, verbose_name='Role')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='map.map', verbose_name='Map')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'unique_together': {('map', 'user')},
            },
        ),
    ]