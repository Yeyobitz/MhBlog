from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib.auth.models import User

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
            
            user_role = request.user.profile.role
            
            # Los admins siempre tienen acceso
            if user_role == 'admin':
                return view_func(request, *args, **kwargs)
            
            # Los moderadores no pueden restringir a otros moderadores o admins
            if 'moderador' in required_roles and user_role == 'moderador':
                # Si la vista es para restringir usuarios, verificar el rol del usuario objetivo
                if 'username' in kwargs:
                    target_user = User.objects.get(username=kwargs['username'])
                    if hasattr(target_user, 'profile') and target_user.profile.role in ['moderador', 'admin']:
                        raise PermissionDenied
            
            # Verificar si el usuario tiene el rol requerido
            if user_role not in required_roles:
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 