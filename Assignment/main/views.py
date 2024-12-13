from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetView
from .forms import LoginForm, SignupForm, EditProfileForm, ChangePasswordForm
from .models import Profile


def index(request):
    """Homepage view."""
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'index.html')


def login(request):
    """User login view."""
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect('login')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        return redirect('profile')
    return render(request, 'login.html', {'form': form})


def signup(request):
    """User registration view."""
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect('login')

    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user)
        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')
    return render(request, 'signup.html', {'form': form})


@login_required
def logout(request):
    """User logout view."""
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def profile(request):
    """User profile view."""
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def dashboard(request):
    """User dashboard view."""
    profile = Profile.objects.get(user=request.user)
    return render(request, 'dash.html', {'profile': profile})


@login_required
def edit_profile(request):
    """Edit user profile."""
    form = EditProfileForm(instance=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        Profile.objects.filter(user=request.user).update()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'editProfile.html', {'form': form})


@login_required
def change_password(request):
    """Change user password."""
    form = ChangePasswordForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        
        update_session_auth_hash(request, request.user)  # Prevents logout after password change
        Profile.objects.filter(user=request.user).update()
        messages.success(request, 'Password changed successfully.')
        return redirect('profile')
    return render(request, 'updatePass.html', {'form': form})


class ForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """Password reset view."""
    email_template_name = 'email_reset.html'
    subject_template_name = 'email_subject.txt'
    success_url = reverse_lazy('login')
    template_name = 'forgot_password.html'
    success_message = "Password reset instructions have been sent to your email."
