# Generated by Django 5.1.2 on 2024-11-26 09:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0046_map_owner_since'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='references',
        ),
        migrations.CreateModel(
            name='MapReference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, verbose_name='Label')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='references', to='library.map', verbose_name='Map')),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.url', verbose_name='URL')),
            ],
        ),
    ]
