# Generated by Django 5.1.1 on 2025-01-28 03:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('administrators', '0001_initial'),
        ('help_types', '0001_initial'),
        ('members', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Help',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limit_date', models.CharField(max_length=20)),
                ('unit_amount', models.IntegerField()),
                ('amount', models.IntegerField()),
                ('comments', models.TextField(max_length=255)),
                ('state', models.IntegerField(default=1)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('administrator_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administrators.administrator')),
                ('help_type_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='help_types.help_type')),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.member')),
            ],
        ),
    ]
