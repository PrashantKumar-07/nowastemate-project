from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    ROLE_CHOICES = [('donor', 'Donor'), ('ngo', 'NGO')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    phone_number = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Donation(models.Model):
    CATEGORY_CHOICES = [
        ('veg', 'Cooked Meal (Veg)'),
        ('non_veg', 'Cooked Meal (Non-Veg)'),
        ('packaged', 'Packaged Food'),
        ('fruits_veg', 'Fruits & Vegetables'),
        ('bakery', 'Bakery Items'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('claimed', 'Claimed'),
        ('completed', 'Completed'),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    food_item = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    pickup_location = models.TextField()
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    pickup_by = models.DateTimeField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_donations')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_item} by {self.donor.username}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

