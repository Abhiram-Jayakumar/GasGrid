from django.db import models

from Admin.models import Gas
from Agent.models import Agent

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    idproof_User = models.ImageField(upload_to='idproof_User/',)
    password = models.CharField(max_length=100)  # Stored in plain text (not secure)
    date_registered = models.DateTimeField(auto_now_add=True)
    
class UserBookGas(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    BOOKING_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ( 'Delivered','Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)  
    gas_product = models.ForeignKey(Gas, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField()  
    booking_date = models.DateTimeField(auto_now_add=True)  
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='Pending')  # Track booking status
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')  # Track payment status