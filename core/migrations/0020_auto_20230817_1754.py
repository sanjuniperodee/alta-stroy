# Generated by Django 2.2 on 2023-08-17 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20230816_0142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='diameter',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='height',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]