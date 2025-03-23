from django.db import models

from Admin.models import Gas

# Create your models here.

class Agent(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=100, unique=True)
    agency_name = models.TextField()
    agency_start_year = models.IntegerField()
    agent_image = models.ImageField(upload_to='agent_images/', blank=True, null=True)
    agent_idproof = models.ImageField(upload_to='idproof_agent/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    password = models.CharField(max_length=100)  # Storing in plain text (not secure)
    date_registered = models.DateTimeField(auto_now_add=True)
    agent_approved_status = models.IntegerField(default=0)
    
    

    
class GasBookAgent(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Delivered", "Delivered"),
        ("Canceled", "Canceled"),
    ]

    PAYMENT_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
    ]

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)  # Agent who booked
    gas_product = models.ForeignKey(Gas, on_delete=models.CASCADE)  # Gas product booked
    quantity = models.PositiveIntegerField()  # Quantity booked
    booking_date = models.DateTimeField(auto_now_add=True)  # Booking date
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total cost
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="Pending")  # Payment status
    booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")  # Booking status
