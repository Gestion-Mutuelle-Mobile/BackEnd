# Generated by Django 5.1.1 on 2024-11-14 09:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operationApp', '0002_borrowing_epargne_obligatorycontribution_refund'),
        ('refunds', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refund',
            name='borrowing_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operationApp.borrowing'),
        ),
    ]
