# Generated by Django 5.1.1 on 2024-11-30 17:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('administrators', '0001_initial'),
        ('members', '0001_initial'),
        ('mutualApp', '0002_session_create_at_alter_exercise_create_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Borrowing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.IntegerField()),
                ('amount_borrowed', models.IntegerField(blank=True, null=True)),
                ('amount_paid', models.IntegerField(default=0)),
                ('amount_to_pay', models.IntegerField(blank=True, null=True)),
                ('payment_date_line', models.DateTimeField(blank=True, null=True)),
                ('state', models.BooleanField(default=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('administrator_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administrators.administrator')),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.member')),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mutualApp.session')),
            ],
        ),
    ]
