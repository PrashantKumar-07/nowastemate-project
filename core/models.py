"""
Database models for the NoWasteMate application.

This file defines the database schema for the project, including user profiles
to distinguish between Donors and NGOs, and the Donation model to track food items.
"""
from django.db import models
from django.contrib.auth.models import User

# Model to extend the built-in User model with roles and verification status
class UserProfile(models.Model):
    """
    Extends Django's built-in User model to add roles.
    Each user is linked to a profile which defines their role and status.
    """
    # Link to the standard User model. If a User is deleted, their profile is too.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Define the roles a user can have
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('ngo', 'NGO'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    # Admin must approve new accounts before they can be used.
    is_approved = models.BooleanField(default=False)
    
    # Simple string representation for the admin panel
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} ({'Approved' if self.is_approved else 'Pending'})"

# Model to store information about each food donation
class Donation(models.Model):
    """
    Represents a single food donation posted by a Donor.
    Tracks the food item, quantity, status, and who donated/claimed it.
    """
    # The user who posted the donation (must be a Donor)
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    
    # The NGO who claimed the donation. Can be null if not yet claimed.
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_donations')

    food_item = models.CharField(max_length=200, help_text="e.g., Vegetable Biryani, Bread Loaves")
    quantity = models.CharField(max_length=100, help_text="e.g., Approx 10 kg, 20 packets")
    pickup_location = models.TextField()
    
    # Tracks the lifecycle of the donation
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('claimed', 'Claimed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    # Timestamps for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"'{self.food_item}' from {self.donor.username} - Status: {self.get_status_display()}"
