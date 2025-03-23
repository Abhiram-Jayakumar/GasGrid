# Generated by Django 5.1.7 on 2025-03-19 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0004_rename_gasproduct_gas'),
        ('Agent', '0002_gasbookagent'),
        ('User', '0002_alter_user_idproof_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBookGas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=150)),
                ('user_email', models.EmailField(max_length=254)),
                ('quantity', models.PositiveIntegerField()),
                ('booking_date', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Agent.agent')),
                ('gas_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Admin.gas')),
            ],
        ),
    ]
