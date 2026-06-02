from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from axes.handlers.proxy import AxesProxyHandler
from axes.models import AccessAttempt
from .forms import UserCreationForm, UserChangeForm, PublicRegistrationForm
from .decorators import admin_required

User = get_user_model()


class CustomLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        axes_locked_message = self._get_axes_locked_message()
        if axes_locked_message:
            context['axes_locked_message'] = axes_locked_message
        return context

    def _get_axes_locked_message(self):
        if self.request.method != 'POST':
            return None

        username = self.request.POST.get('username')
        if not username:
            return None

        # Show a friendly unlock message if Axes has locked this username.
        try:
            if AxesProxyHandler.is_locked(self.request, {'username': username}):
                return (
                    'Your account has been temporarily locked after too many failed login attempts. '
                    'Use the "Forgot password?" link below to reset your password and unlock your account immediately, '
                    'or wait 30 minutes for the lockout to expire.'
                )
        except Exception:
            pass

        return None


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            user = form.user
            AccessAttempt.objects.filter(username__iexact=user.username).delete()
        except Exception:
            pass
        return response


def register(request):
    """Allow visitors to create a public viewer account."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PublicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'viewer'
            user.is_staff = False
            user.is_superuser = False
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = PublicRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


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
