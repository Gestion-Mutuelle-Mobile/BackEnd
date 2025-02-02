# Generated by Django 5.1.1 on 2025-01-28 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest_per_borrow', models.IntegerField(default=10)),
                ('inscription_per_member', models.IntegerField(default=10000)),
                ('no_months_to_pay_0_to_300K', models.IntegerField(default=3)),
                ('no_months_to_pay_300_to_600K', models.IntegerField(default=6)),
                ('monthly_contribution_per_member', models.IntegerField(default=20000)),
            ],
        ),
    ]
