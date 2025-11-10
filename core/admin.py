from django.contrib import admin
from .models import UserProfile, Donation, ContactMessage

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_display', 'phone_number', 'role', 'is_approved')
    list_filter = ('is_approved', 'role')
    actions = ['approve_users']

    fieldsets = (
        ('User Credentials', {
            'fields': ('user', 'email_detail_display'),
        }),
        ('Profile Details', {
            'fields': ('role', 'phone_number'),
        }),
        ('Authorization Status', {
            'fields': ('is_approved',),
            'description': 'Check this box to grant access to the platform.',
        }),
    )
    
    readonly_fields = ('email_detail_display',)

    def email_display(self, obj):
        return obj.user.email
    email_display.short_description = "Email Address"

    def email_detail_display(self, obj):
        return obj.user.email
    email_detail_display.short_description = "Email Address"

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
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