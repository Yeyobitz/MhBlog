from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            
            if not hasattr(request.user, 'profile'):
                raise PermissionDenied
            
            if isinstance(roles, str):
                required_roles = [roles]
            else:
                required_roles = roles
            
            if request.user.profile.role not in required_roles and 'admin' not in required_roles:
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 