# Generated by Django 5.0.4 on 2025-03-26 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0012_userproductbooking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproductbooking',
            name='booking_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('Delivered', 'Delivered')], default='confirmed', max_length=20),
        ),
    ]
