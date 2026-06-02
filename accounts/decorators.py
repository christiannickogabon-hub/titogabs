from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def role_required(allowed_roles):
    """
    Decorator to enforce role-based access control.
    Usage: @role_required(['admin', 'dispatcher'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.role not in allowed_roles:
                return HttpResponseForbidden('You do not have permission to access this resource.')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to require admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_superuser and request.user.role != 'admin':
            return HttpResponseForbidden('Only administrators can access this resource.')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def superuser_required(view_func):
    """Decorator to require Django superuser access."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not request.user.is_superuser:
            return HttpResponseForbidden('Only the superadmin can access this resource.')

        return view_func(request, *args, **kwargs)
    return wrapper


def dispatcher_or_admin_required(view_func):
    """Decorator to require dispatcher or admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if request.user.role not in ['admin', 'dispatcher']:
            return HttpResponseForbidden('Only dispatchers and administrators can access this resource.')
        
        return view_func(request, *args, **kwargs)
    return wrapper
