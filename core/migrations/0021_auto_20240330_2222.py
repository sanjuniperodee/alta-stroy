# Generated by Django 2.2 on 2024-03-30 22:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20230817_1754'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='articul',
        ),
        migrations.RemoveField(
            model_name='item',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='item',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='item',
            name='decor_obrabotka',
        ),
        migrations.RemoveField(
            model_name='item',
            name='design',
        ),
        migrations.RemoveField(
            model_name='item',
            name='diameter',
        ),
        migrations.RemoveField(
            model_name='item',
            name='faska',
        ),
        migrations.RemoveField(
            model_name='item',
            name='max_height',
        ),
        migrations.RemoveField(
            model_name='item',
            name='min_height',
        ),
        migrations.RemoveField(
            model_name='item',
            name='selection',
        ),
        migrations.RemoveField(
            model_name='item',
            name='wood_type',
        ),
        migrations.DeleteModel(
            name='Brand',
        ),
    ]