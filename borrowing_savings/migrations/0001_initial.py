# Generated by Django 5.1.1 on 2025-01-28 03:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('operationApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Borrowing_Saving',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent', models.FloatField(max_length=10)),
                ('borrowing_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operationApp.borrowing')),
                ('epargne_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='operationApp.epargne')),
            ],
        ),
    ]
