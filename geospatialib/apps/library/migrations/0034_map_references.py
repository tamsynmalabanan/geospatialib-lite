# Generated by Django 5.1.2 on 2024-11-21 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0033_map_headline'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='references',
            field=models.ManyToManyField(blank=True, related_name='maps', to='library.url', verbose_name='References'),
        ),
    ]
