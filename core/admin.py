"""
Configuration for the Django admin interface for the 'core' app.

This file is used to register the database models with the Django admin site,
making them manageable for the superuser. We customize the display to show
key information and allow for easy approval of new users.
"""
from django.contrib import admin
from .models import UserProfile, Donation

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Customizes the admin view for UserProfile model.
    """
    # Fields to display in the list view of user profiles
    list_display = ('user', 'role', 'is_approved')
    # Filters to allow sorting by approval status and role
    list_filter = ('is_approved', 'role')
    # Action to approve selected users in bulk
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        """
        Custom admin action to approve selected user profiles.
        """
        queryset.update(is_approved=True)
    approve_users.short_description = "Approve selected users"

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """
    Customizes the admin view for Donation model.
    """
    # Fields to display in the list view of donations
    list_display = ('food_item', 'donor', 'status', 'claimed_by', 'created_at')
    # Filters to allow sorting by status
    list_filter = ('status', 'created_at')
    # Fields that can be searched
    search_fields = ('food_item', 'donor__username', 'claimed_by__username')
