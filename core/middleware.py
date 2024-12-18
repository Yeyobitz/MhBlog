from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import UserRestriction

class UserRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            # Las restricciones no se aplican a moderadores y admins
            if request.user.profile.role in ['moderador', 'admin']:
                return self.get_response(request)
            
            # Verificar restricciones de posts
            if request.path.startswith('/blog/crear/'):
                active_restriction = UserRestriction.objects.filter(
                    user=request.user,
                    restriction_type='posts',
                    end_date__gt=timezone.now()
                ).first()
                
                if active_restriction:
                    end_date_str = active_restriction.end_date.strftime("%d/%m/%Y %H:%M")
                    messages.error(
                        request,
                        f'No puedes crear posts hasta el {end_date_str}. '
                        f'Razón: {active_restriction.reason}'
                    )
                    return redirect('core:index')
            
            # Verificar restricciones de comentarios
            if request.method == 'POST' and 'contenido' in request.POST:
                active_restriction = UserRestriction.objects.filter(
                    user=request.user,
                    restriction_type='comments',
                    end_date__gt=timezone.now()
                ).first()
                
                if active_restriction:
                    end_date_str = active_restriction.end_date.strftime("%d/%m/%Y %H:%M")
                    messages.error(
                        request,
                        f'No puedes comentar hasta el {end_date_str}. '
                        f'Razón: {active_restriction.reason}'
                    )
                    return redirect(request.META.get('HTTP_REFERER', 'core:index'))

        response = self.get_response(request)
        return response 