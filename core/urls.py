"""
URL patterns for the 'core' application.

This file maps URLs to their corresponding view functions defined in views.py.
It defines the endpoints for user registration, login, dashboards, and donation management.
"""
from django.urls import path
from . import views

# The name argument is used for URL reversing, allowing us to refer to URLs by name in templates
urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Donation Management
    path('donate/', views.post_donation_view, name='post_donation'),
    path('donations/', views.view_donations_view, name='view_donations'),
    path('donations/claim/<int:donation_id>/', views.claim_donation_view, name='claim_donation'),
]
