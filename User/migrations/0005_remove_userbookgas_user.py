# Generated by Django 5.1.7 on 2025-03-19 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_userbookgas_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbookgas',
            name='user',
        ),
    ]
