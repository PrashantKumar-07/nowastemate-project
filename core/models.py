from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (('donor', 'Donor'), ('ngo', 'NGO'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=10)
    is_approved = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def recalculate_rating(self):
        all_my_reviews = self.user.reviews_received.all()
        if all_my_reviews:
            self.average_rating = all_my_reviews.aggregate(Avg('rating'))['rating__avg']
        else:
            self.average_rating = 0.0
        self.save()

class Donation(models.Model):
    CATEGORY_CHOICES = [
        ('cooked', 'Cooked Meal'),
        ('packaged', 'Packaged Food'),
        ('bakery', 'Bakery Items'),
        ('produce', 'Fruits & Vegetables'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('claimed', 'Claimed'),
        ('completed', 'Completed'),
    ]
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_donations')
    food_item = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='other')
    quantity = models.CharField(max_length=100)
    pickup_location = models.TextField()
    pickup_by = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.food_item

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class Review(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('donation', 'reviewer')

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewed_user.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

    class Meta:
        ordering = ['-created_at']