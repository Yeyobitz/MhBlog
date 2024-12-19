from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib.auth.models import User

def group_required(groups):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            
            if isinstance(groups, str):
                required_groups = [groups]
            else:
                required_groups = groups
            
            # Los superusuarios siempre tienen acceso
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Los moderadores no pueden restringir a otros moderadores o admins
            if 'Moderators' in required_groups and request.user.groups.filter(name='Moderators').exists():
                # Si la vista es para restringir usuarios, verificar el grupo del usuario objetivo
                if 'username' in kwargs:
                    target_user = User.objects.get(username=kwargs['username'])
                    if target_user.groups.filter(name='Moderators').exists() or target_user.is_superuser:
                        raise PermissionDenied
            
            # Verificar si el usuario pertenece a alguno de los grupos requeridos
            if not request.user.groups.filter(name__in=required_groups).exists():
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 