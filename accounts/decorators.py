from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Restrict a view to users with one of the given roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard:home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def owner_required(view_func):
    return role_required('owner')(view_func)


def supervisor_required(view_func):
    return role_required('owner', 'supervisor')(view_func)


def employee_required(view_func):
    return role_required('owner', 'supervisor', 'employee')(view_func)
