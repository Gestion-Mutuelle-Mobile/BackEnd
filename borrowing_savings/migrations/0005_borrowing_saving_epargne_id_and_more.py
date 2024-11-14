# Generated by Django 5.1.1 on 2024-11-14 09:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('borrowing_savings', '0004_remove_borrowing_saving_saving_id'),
        ('operationApp', '0002_borrowing_epargne_obligatorycontribution_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowing_saving',
            name='epargne_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operationApp.epargne'),
        ),
        migrations.AlterField(
            model_name='borrowing_saving',
            name='borrowing_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operationApp.borrowing'),
        ),
    ]
