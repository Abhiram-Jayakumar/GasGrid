# Generated by Django 5.0.4 on 2025-03-25 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agent', '0004_gasproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gasproduct',
            name='quantity_available',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
