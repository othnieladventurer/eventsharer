from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps






def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')
            if request.user.role not in allowed_roles:
                # Optional: Redirect or raise 403
                return redirect('support:index')  # or 'dashboard:dashboard'
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator




    
    