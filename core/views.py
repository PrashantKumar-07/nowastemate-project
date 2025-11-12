from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate
import json
from datetime import timedelta

from .models import UserProfile, Donation, ContactMessage, Review, Notification
from .forms import CustomUserCreationForm


def home_view(request):
    return render(request, 'core/home.html')


def register_view(request):
    
    selected_role = request.POST.get('role') if request.method == 'POST' else request.GET.get('role', '')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid() and selected_role in ['donor', 'ngo']:
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            phone_number = form.cleaned_data.get('phone_number')
            UserProfile.objects.create(user=user, role=selected_role, phone_number=phone_number)

            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    else: 
        form = CustomUserCreationForm()
        
    context = {
        'form': form,
        'selected_role': selected_role
    }
    return render(request, 'core/register.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if hasattr(user, 'userprofile') and user.userprofile.is_approved:
                    login(request, user)
                    messages.info(request, f'Welcome back, {username}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Your account is pending approval from the administrator.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


@login_required
def dashboard_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        if request.user.is_superuser:
            return redirect('/admin/')
        else:
            messages.error(request, "Your user profile could not be found.")
            return redirect('home')

    if profile.role == 'donor':
        donations = Donation.objects.filter(donor=request.user).order_by('-created_at')
        donation_ids = [d.id for d in donations]
        
        reviews_for_me_qs = Review.objects.filter(
            donation_id__in=donation_ids, 
            reviewed_user=request.user
        )
        reviews_for_me = {review.donation_id: review for review in reviews_for_me_qs}

        reviews_by_me = Review.objects.filter(
            donation_id__in=donation_ids, 
            reviewer=request.user
        ).values_list('donation_id', flat=True)

        for d in donations:
            if d.id in reviews_for_me:
                d.review_for_me = reviews_for_me[d.id]
            if d.id in reviews_by_me:
                d.has_review_by_me = True
                
        return render(request, 'core/donor_dashboard.html', {'donations': donations})

    elif profile.role == 'ngo':
        claimed_donations = Donation.objects.filter(claimed_by=request.user).order_by('-created_at')
        donation_ids = [d.id for d in claimed_donations]

        reviews_for_me_qs = Review.objects.filter(
            donation_id__in=donation_ids, 
            reviewed_user=request.user
        )
        reviews_for_me = {review.donation_id: review for review in reviews_for_me_qs}

        reviews_by_me = Review.objects.filter(
            donation_id__in=donation_ids, 
            reviewer=request.user
        ).values_list('donation_id', flat=True)
        
        for d in claimed_donations:
            if d.id in reviews_for_me:
                d.review_for_me = reviews_for_me[d.id]
            if d.id in reviews_by_me:
                d.has_review_by_me = True

        return render(request, 'core/ngo_dashboard.html', {'claimed_donations': claimed_donations})
    
    return redirect('home')


@login_required
def post_donation_view(request):
    if request.user.userprofile.role != 'donor':
        return redirect('dashboard')

    if request.method == 'POST':
        food = request.POST.get('food_item')
        cat = request.POST.get('category')
        qty = request.POST.get('quantity')
        pickup_time_str = request.POST.get('pickup_by')
        addr = request.POST.get('pickup_location')
        
        if all([food, cat, qty, pickup_time_str, addr]):
            
            naive_datetime = timezone.datetime.fromisoformat(pickup_time_str)
            aware_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())

            new_donation = Donation.objects.create(
                donor=request.user, 
                food_item=food, 
                category=cat,
                quantity=qty, 
                pickup_by=aware_datetime, 
                pickup_location=addr
            )
            
            try:
                all_ngos = User.objects.filter(userprofile__role='ngo', userprofile__is_approved=True)
                ngo_email_list = []
                
                for ngo in all_ngos:
                    if ngo.email:
                        ngo_email_list.append(ngo.email)
                    Notification.objects.create(
                        user=ngo,
                        message=f"New donation from {request.user.username}: {new_donation.food_item}",
                        link="/donations/"
                    )

                if ngo_email_list:
                    subject = f"New Donation Available: {new_donation.food_item}"
                    message = f"A new food donation has been posted on NoWasteMate: {new_donation.food_item}"
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=ngo_email_list,
                        fail_silently=False, 
                    )
            except Exception as e:
                pass 
            
            messages.success(request, 'Your donation has been posted and all NGOs have been notified!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    categories = Donation.CATEGORY_CHOICES
    return render(request, 'core/post_donation.html', {'categories': categories})


@login_required
def view_donations_view(request):
    if request.user.userprofile.role != 'ngo':
        return redirect('dashboard')
        
    donations = Donation.objects.filter(status='available')

    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')

    if keyword:
        donations = donations.filter(food_item__icontains=keyword)
    
    if category:
        donations = donations.filter(category=category)
        
    if location:
        donations = donations.filter(pickup_location__icontains=location)

    donations = donations.order_by('-created_at')
    
    context = {
        'donations': donations,
        'categories': Donation.CATEGORY_CHOICES,
        'search_keyword': keyword,
        'search_category': category,
        'search_location': location,
    }
    return render(request, 'core/view_donations.html', context)


@login_required
def claim_donation_view(request, donation_id):
    if request.user.userprofile.role != 'ngo':
        return redirect('dashboard')

    donation = get_object_or_404(Donation, id=donation_id, status='available')
    
    donation.claimed_by = request.user
    donation.status = 'claimed'
    donation.save()
    
    if donation.donor.email:
        Notification.objects.create(
            user=donation.donor,
            message=f"Your donation '{donation.food_item}' was claimed by {request.user.username}.",
            link="/dashboard/"
        )
        subject = f"Your donation '{donation.food_item}' has been claimed!"
        message = f"Great news! Your donation has been claimed by the NGO: {donation.claimed_by.username}."
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[donation.donor.email],
            fail_silently=True,
        )
    
    messages.success(request, f"You have successfully claimed the donation: '{donation.food_item}'.")
    return redirect('dashboard')


@login_required
def complete_donation_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user)

    if donation.status == 'claimed':
        donation.status = 'completed'
        donation.save()
        
        if donation.claimed_by and donation.claimed_by.email:
            Notification.objects.create(
                user=donation.claimed_by,
                message=f"Donation of '{donation.food_item}' is now complete. Please leave a review!",
                link="/dashboard/"
            )
            subject = f"Donation Completed: {donation.food_item}"
            message = f"The donation '{donation.food_item}' from {donation.donor.username} has been marked as completed."
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[donation.claimed_by.email],
                fail_silently=True,
            )
            
        messages.success(request, f"Thank you! You have marked the donation '{donation.food_item}' as completed.")
    else:
        messages.error(request, "This donation cannot be marked as completed at this time.")
    
    return redirect('dashboard')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not all([name, email, subject, message]):
            messages.error(request, "Please fill out all fields.")
            return render(request, 'core/contact.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'core/contact.html')

        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message
        )

        admin_subject = f"New Contact Message from {name}: {subject}"
        admin_message = f"Message from: {name} ({email})\n\n{message}"
        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['admin@nowastemate.com'],
        )

        user_subject = "Thank you for contacting NoWasteMate"
        user_message = f"Hi {name},\n\nWe have received your message and will get back to you soon."
        send_mail(
            subject=user_subject,
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(request, "Thank you for your message! It has been sent successfully.")
        return redirect('contact')
            
    return render(request, 'core/contact.html')


@login_required
def add_review_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    user_profile = request.user.userprofile
    
    if donation.status != 'completed':
        messages.error(request, "You can only review completed donations.")
        return redirect('dashboard')
    
    user_to_review = None
    if user_profile.role == 'donor' and donation.claimed_by:
        user_to_review = donation.claimed_by
    elif user_profile.role == 'ngo' and donation.donor:
        user_to_review = donation.donor
    else:
        messages.error(request, "Cannot determine who to review for this donation.")
        return redirect('dashboard')
    
    try:
        Review.objects.get(donation=donation, reviewer=request.user)
        messages.warning(request, "You have already reviewed this donation.")
        return redirect('dashboard')
    except ObjectDoesNotExist:
        pass

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating:
            messages.error(request, "You must select a rating.")
        else:
            new_review = Review.objects.create(
                donation=donation,
                reviewer=request.user,
                reviewed_user=user_to_review,
                rating=rating,
                comment=comment
            )
            
            user_to_review.userprofile.recalculate_rating()
            
            Notification.objects.create(
                user=user_to_review,
                message=f"{request.user.username} left you a {rating}-star review!",
                link="/dashboard/"
            )
            
            messages.success(request, f"Thank you! Your review for {user_to_review.username} has been submitted.")
            return redirect('dashboard')
    
    context = {
        'donation': donation,
        'user_to_review': user_to_review
    }
    return render(request, 'core/add_review.html', context)



def impact_analytics_view(request):
    
    total_donations = Donation.objects.filter(status='completed').count()
    total_donors = UserProfile.objects.filter(role='donor', is_approved=True).count()
    total_ngos = UserProfile.objects.filter(role='ngo', is_approved=True).count()

    min_reviews = 3
    
    donors_with_reviews = UserProfile.objects.annotate(
        review_count=Count('user__reviews_received')
    )
    ngos_with_reviews = UserProfile.objects.annotate(
        review_count=Count('user__reviews_received')
    )
    
    avg_donor_rating = donors_with_reviews.filter(
        role='donor', 
        review_count__gte=min_reviews
    ).aggregate(Avg('average_rating'))['average_rating__avg'] or 0.0
    
    avg_ngo_rating = ngos_with_reviews.filter(
        role='ngo', 
        review_count__gte=min_reviews
    ).aggregate(Avg('average_rating'))['average_rating__avg'] or 0.0

    top_donors_data = User.objects.filter(donations__status='completed').annotate(
        donation_count=Count('donations')
    ).order_by('-donation_count')[:5]
    
    donor_labels = [user.username for user in top_donors_data]
    donor_counts = [user.donation_count for user in top_donors_data]
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    donations_over_time = (
        Donation.objects.filter(created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    time_labels = [item['date'].strftime('%b %d') for item in donations_over_time]
    time_counts = [item['count'] for item in donations_over_time]

    context = {
        'total_donations': total_donations,
        'total_donors': total_donors,
        'total_ngos': total_ngos,
        'avg_donor_rating': avg_donor_rating,
        'avg_ngo_rating': avg_ngo_rating,
        'min_reviews_for_rating': min_reviews,
        
        'donor_labels': json.dumps(donor_labels),
        'donor_counts': json.dumps(donor_counts),
        
        'time_labels': json.dumps(time_labels),
        'time_counts': json.dumps(time_counts),
    }
    return render(request, 'core/impact_analytics.html', context)


@login_required
def mark_notifications_as_read_view(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))