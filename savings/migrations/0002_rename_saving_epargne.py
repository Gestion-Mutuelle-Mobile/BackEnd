# Generated by Django 5.1.1 on 2024-11-14 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0001_initial'),
        ('members', '0001_initial'),
        ('mutualApp', '0001_initial'),
        ('savings', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Saving',
            new_name='Epargne',
        ),
    ]
