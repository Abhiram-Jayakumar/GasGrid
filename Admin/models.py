from django.db import models

# Create your models here.


class Admintable(models.Model):
    email=models.EmailField(unique=True,null=True)
    password=models.CharField(max_length=50,unique=True)
    
    
class Gas(models.Model):
    CATEGORY_CHOICES = [
        ('Industrial', 'Industrial'),
        ('Commercial', 'Commercial'),
        ('Medical', 'Medical'),
    ]

    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(help_text="Quantity available in stock",null=True, blank=True)
    initial_quantity = models.PositiveIntegerField(help_text="Initial quantity added")
    weight= models.CharField(max_length=50)
    retailer_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    added_on = models.DateTimeField(auto_now_add=True)
    
