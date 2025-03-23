# Generated by Django 5.0.4 on 2025-03-21 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agent', '0002_gasbookagent'),
    ]

    operations = [
        migrations.AddField(
            model_name='gasbookagent',
            name='booking_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Delivered', 'Delivered'), ('Canceled', 'Canceled')], default='Pending', max_length=20),
        ),
        migrations.AddField(
            model_name='gasbookagent',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending', max_length=20),
        ),
        migrations.AddField(
            model_name='gasbookagent',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
