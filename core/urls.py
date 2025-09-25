"""
URL patterns for the 'core' application.
...
"""
from django.urls import path
from . import views

# The name argument is used for URL reversing
urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('contact/', views.contact_view, name='contact'),
    
    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Donation Management
    path('donate/', views.post_donation_view, name='post_donation'),
    path('donations/', views.view_donations_view, name='view_donations'),
    path('donations/claim/<int:donation_id>/', views.claim_donation_view, name='claim_donation'),
]

