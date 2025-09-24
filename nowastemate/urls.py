"""
Main URL configuration for the NoWasteMate project.

This file routes incoming URL requests. It includes the Django admin URLs
and routes all other requests to the 'core' application's URL configuration.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # The Django admin site
    path('admin/', admin.site.urls),
    
    # Include all URLs from the 'core' app
    path('', include('core.urls')),
]