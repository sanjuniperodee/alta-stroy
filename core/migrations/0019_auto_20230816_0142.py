# Generated by Django 2.2 on 2023-08-15 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_item_decor_obrabotka'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='length',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='thickness',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='width',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]