"""
Database models for the NoWasteMate application.
Includes models for User Profiles and Food Donations.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Model to extend the built-in User model with roles, contact info, and verification status
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (('donor', 'Donor'), ('ngo', 'NGO'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    # NEW: Contact number for verification and coordination
    phone_number = models.CharField(max_length=15, help_text="Enter your 10-digit phone number.")

    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} ({'Approved' if self.is_approved else 'Pending'})"

# Model to store information about each food donation
class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_donations')

    # NEW: Food category for better filtering
    CATEGORY_CHOICES = (
        ('cooked_meal', 'Cooked Meal'),
        ('bakery_goods', 'Bakery Goods'),
        ('produce', 'Fruits & Vegetables'),
        ('packaged_items', 'Packaged & Canned Goods'),
        ('other', 'Other'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    food_item = models.CharField(max_length=200, help_text="e.g., Vegetable Biryani, Bread Loaves")
    quantity = models.CharField(max_length=100, help_text="e.g., Approx 10 kg, 20 packets")
    pickup_location = models.TextField()

    # NEW: Expiry date and time for pickup
    pickup_by = models.DateTimeField(help_text="The food must be picked up before this date and time.")

    STATUS_CHOICES = (('available', 'Available'), ('claimed', 'Claimed'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"'{self.food_item}' from {self.donor.username} - Status: {self.get_status_display()}"

