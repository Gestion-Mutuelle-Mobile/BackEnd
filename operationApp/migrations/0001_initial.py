# Generated by Django 5.1.1 on 2024-11-14 00:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('administrators', '0001_initial'),
        ('members', '0001_initial'),
        ('mutualApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('administrator_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administrators.administrator')),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mutualApp.session')),
            ],
        ),
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('operation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='operationApp.operation')),
                ('state', models.BooleanField(default=True)),
                ('member_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='members.member')),
            ],
            bases=('operationApp.operation',),
        ),
        migrations.CreateModel(
            name='Help',
            fields=[
                ('operation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='operationApp.operation')),
                ('limit_date', models.DateField()),
                ('amount_expected', models.IntegerField()),
                ('comments', models.TextField(max_length=255)),
                ('state', models.BooleanField(default=True)),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operation_help_set', to='members.member')),
            ],
            bases=('operationApp.operation',),
        ),
        migrations.CreateModel(
            name='PersonalContribution',
            fields=[
                ('contribution_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='operationApp.contribution')),
                ('date', models.CharField(max_length=20)),
                ('amount', models.IntegerField(default=0)),
                ('help_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='operationApp.help')),
            ],
            bases=('operationApp.contribution',),
        ),
    ]
