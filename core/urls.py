from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact_view, name='contact'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    path('donate/', views.post_donation_view, name='post_donation'),
    path('donations/', views.view_donations_view, name='view_donations'),
    path('donations/claim/<int:donation_id>/', views.claim_donation_view, name='claim_donation'),
    path('donations/complete/<int:donation_id>/', views.complete_donation_view, name='complete_donation'),

    path('review/add/<int:donation_id>/', views.add_review_view, name='add_review'),
    
    path('impact/', views.impact_analytics_view, name='impact_analytics'),
    
    path('notifications/mark-as-read/', views.mark_notifications_as_read_view, name='mark_notifications_as_read'),
]