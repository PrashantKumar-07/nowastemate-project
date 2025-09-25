"""
Custom forms for the 'core' application.

This file defines custom form classes to extend the default Django forms.
The CustomUserCreationForm adds a 'phone_number' field to the user
registration process, ensuring that this crucial information is collected.
"""
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form that extends the default UserCreationForm to include
    a phone number field.
    """
    phone_number = forms.CharField(max_length=15, required=True, help_text='Enter your 10-digit mobile number.')

    class Meta(UserCreationForm.Meta):
        # We don't need to add a model here because we save the fields manually in the view.
        fields = UserCreationForm.Meta.fields + ('phone_number',)