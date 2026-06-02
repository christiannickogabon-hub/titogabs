from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserCreationForm, UserChangeForm
from .decorators import admin_required

User = get_user_model()


def home(request):
    """Home page - redirect to dashboard if authenticated"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


@login_required
def profile(request):
    """View user profile"""
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def logout_view(request):
    """Log the current user out and return to the login screen."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')

    return redirect('dashboard')


@login_required
@admin_required
def user_list(request):
    """List all users (Admin only)"""
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
@admin_required
def user_create(request):
    """Create a new user (Admin only)"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_list')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/user_create.html', context)


@login_required
@admin_required
def user_update(request, pk):
    """Update user (Admin only)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = UserChangeForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'accounts/user_update.html', context)
