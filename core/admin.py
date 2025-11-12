from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, Donation, ContactMessage, Notification, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'phone_number', 'role', 'is_approved', 'average_rating')
    list_filter = ('is_approved', 'role')
    actions = ['approve_users']
    search_fields = ('user__username', 'user__email', 'phone_number')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    fieldsets = (
        ('User Credentials', {
            'fields': ('user', 'get_email'), 
        }),
        ('Profile Details', {
            'fields': ('role', 'phone_number', 'average_rating'),
        }),
        ('Authorization Status', {
            'fields': ('is_approved',),
        }),
    )
    
    readonly_fields = ('user', 'get_email', 'average_rating')

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        
        for profile in queryset:
            user = profile.user
            
            Notification.objects.create(
                user=user,
                message="Welcome! Your account has been approved.",
                link="/dashboard/"
            )

            if user.email:
                user_subject = "Your NoWasteMate Account is Approved!"
                user_message = f"Hi {user.username},\n\nGood news! Your account on NoWasteMate has been approved."
                send_mail(
                    subject=subject,
                    message=user_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            
    approve_users.short_description = "Approve selected users"

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('food_item', 'donor', 'status', 'category', 'pickup_by')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('food_item', 'donor__username')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent_at')
    readonly_fields = ('name', 'email', 'subject', 'message', 'sent_at')
    actions = ['delete_selected_messages']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def delete_selected_messages(self, request, queryset):
        queryset.delete()
    delete_selected_messages.short_description = "Delete selected contact messages"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('donation', 'reviewer', 'reviewed_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('donation__food_item', 'reviewer__username', 'reviewed_user__username')