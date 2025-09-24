"""
Views for the 'core' application, containing the business logic.

This file handles web requests and returns web responses. Each function
corresponds to a page or an action on the site, such as user registration,
logging in, displaying dashboards, and handling food donations.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile, Donation
from django.contrib import messages

# Home page view
def home_view(request):
    """Renders the landing page."""
    return render(request, 'core/home.html')

# User Registration View
def register_view(request):
    """Handles new user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        role = request.POST.get('role')
        if form.is_valid() and role in ['donor', 'ngo']:
            user = form.save()
            # Create a UserProfile linked to the new user
            UserProfile.objects.create(user=user, role=role)
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

# User Login View
def login_view(request):
    """Handles user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if the user's profile is approved by the admin
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

# User Logout View
def logout_view(request):
    """Logs the user out and redirects to the home page."""
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

# Dashboard View - Redirects user based on their role
@login_required
def dashboard_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # This handles users without a profile (like the superuser)
        if request.user.is_superuser:
            messages.info(request, "Admin users do not have a dashboard. You have been redirected to the admin panel.")
            return redirect('/admin/') # Redirect superuser to the admin panel
        else:
            # Handle other rare cases if needed
            messages.error(request, "Your user profile is not set up correctly. Please contact support.")
            return redirect('home')

    if user_profile.role == 'donor':
        # Donor's dashboard logic...
        donations = Donation.objects.filter(donor=request.user).order_by('-created_at')
        return render(request, 'core/donor_dashboard.html', {'donations': donations})
    elif user_profile.role == 'ngo':
        # NGO's dashboard logic...
        claimed_donations = Donation.objects.filter(claimed_by=request.user).order_by('-updated_at')
        return render(request, 'core/ngo_dashboard.html', {'claimed_donations': claimed_donations})
    
    return redirect('home')

# View for Donors to post a new donation
@login_required
def post_donation_view(request):
    """Allows authenticated donors to post a new food donation."""
    # Ensure only users with the 'donor' role can access this page
    if not request.user.userprofile.role == 'donor':
        messages.error(request, "Only donors can post donations.")
        return redirect('dashboard')

    if request.method == 'POST':
        food_item = request.POST.get('food_item')
        quantity = request.POST.get('quantity')
        pickup_location = request.POST.get('pickup_location')
        
        if food_item and quantity and pickup_location:
            Donation.objects.create(
                donor=request.user,
                food_item=food_item,
                quantity=quantity,
                pickup_location=pickup_location
            )
            messages.success(request, 'Your donation has been posted successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'core/post_donation.html')

# View for NGOs to see all available donations
@login_required
def view_donations_view(request):
    """Allows authenticated NGOs to see all available food donations."""
    # Ensure only users with the 'ngo' role can access this page
    if not request.user.userprofile.role == 'ngo':
        messages.error(request, "Only NGOs can view and claim donations.")
        return redirect('dashboard')
        
    available_donations = Donation.objects.filter(status='available').order_by('-created_at')
    return render(request, 'core/view_donations.html', {'donations': available_donations})

# View for NGOs to claim a donation
@login_required
def claim_donation_view(request, donation_id):
    """Allows an NGO to claim a specific, available donation."""
    # Ensure only NGOs can claim
    if not request.user.userprofile.role == 'ngo':
        messages.error(request, "Only NGOs can claim donations.")
        return redirect('dashboard')

    donation = get_object_or_404(Donation, id=donation_id, status='available')
    
    # Update the donation status and assign it to the claiming NGO
    donation.claimed_by = request.user
    donation.status = 'claimed'
    donation.save()
    
    messages.success(request, f"You have successfully claimed the donation: '{donation.food_item}'.")
    return redirect('dashboard')