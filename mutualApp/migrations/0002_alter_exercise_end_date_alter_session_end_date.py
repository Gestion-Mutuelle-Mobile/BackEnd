# Generated by Django 5.1.1 on 2025-01-28 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mutualApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='end_date',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='end_date',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
