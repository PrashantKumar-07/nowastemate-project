from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import UserProfile, Donation, ContactMessage
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
        return render(request, 'core/donor_dashboard.html', {'donations': donations})
    elif profile.role == 'ngo':
        claimed_donations = Donation.objects.filter(claimed_by=request.user).order_by('-updated_at')
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
        pickup_time = request.POST.get('pickup_by')
        addr = request.POST.get('pickup_location')
        
        if all([food, cat, qty, pickup_time, addr]):
            Donation.objects.create(
                donor=request.user, food_item=food, category=cat,
                quantity=qty, pickup_by=pickup_time, pickup_location=addr
            )
            messages.success(request, 'Your donation has been posted!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    categories = Donation.CATEGORY_CHOICES
    return render(request, 'core/post_donation.html', {'categories': categories})


@login_required
def view_donations_view(request):
    if request.user.userprofile.role != 'ngo':
        return redirect('dashboard')
        
    available = Donation.objects.filter(status='available').order_by('-created_at')
    return render(request, 'core/view_donations.html', {'donations': available})


@login_required
def claim_donation_view(request, donation_id):
    if request.user.userprofile.role != 'ngo':
        return redirect('dashboard')

    donation = get_object_or_404(Donation, id=donation_id, status='available')
    
    donation.claimed_by = request.user
    donation.status = 'claimed'
    donation.save()
    
    messages.success(request, f"You have successfully claimed the donation: '{donation.food_item}'.")
    return redirect('dashboard')


@login_required
def complete_donation_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user)

    if donation.status == 'claimed':
        donation.status = 'completed'
        donation.save()
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
        user_message = f"Hi {name},\n\nWe have received your message and will get back to you soon.\n\nBest regards,\nThe NoWasteMate Team"
        send_mail(
            subject=user_subject,
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(request, "Thank you for your message! It has been sent successfully.")
        return redirect('contact')
            
    return render(request, 'core/contact.html')