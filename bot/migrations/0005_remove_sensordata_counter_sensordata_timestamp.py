# Generated by Django 5.1.5 on 2025-01-19 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_sensordata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensordata',
            name='counter',
        ),
        migrations.AddField(
            model_name='sensordata',
            name='timestamp',
            field=models.DateTimeField(null=True),
        ),
    ]
