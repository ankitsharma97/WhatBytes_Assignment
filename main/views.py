from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin


def index(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'index.html')


def login(request):
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect('login')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')
    
    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password1')

        if not all([name, email, username, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        user = User.objects.create_user(
            username=username, 
            password=password, 
            email=email, 
            first_name=name
        )
        profile = Profile.objects.create(user=user)
        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')
    
    return render(request, 'signup.html')


@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'profile': profile
    }
    return render(request, 'profile.html', context)


@login_required
def dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'dash.html', context)


@login_required
def edit_profile(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        if not all([name, email]):
            messages.error(request, 'Both name and email are required.')
            return redirect('edit_profile')

        request.user.first_name = name
        request.user.email = email

        request.user.save()
        profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    
    return render(request, 'editProfile.html', {'user': request.user, 'profile': profile})


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not all([old_password, new_password, confirm_password]):
            messages.error(request, 'All password fields are required.')
            return redirect('passchange')  
        
        if new_password != confirm_password:
            messages.error(request, 'New password and confirmation do not match.')
            return redirect('passchange')

        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()

            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Old password is incorrect.')
            return redirect('passchange')  

    return render(request, 'updatePass.html')


class ForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    email_template_name = 'email_reset.html'
    subject_template_name = 'email_subject.txt'
    success_url = reverse_lazy('login')
    template_name = 'forgot_password.html'
    success_message = "Password reset instructions have been sent to your email."
