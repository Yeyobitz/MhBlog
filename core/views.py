from django.shortcuts import render
from blog.models import EntradaBlog, Element, Ailment, Game
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger as InvalidPage
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Count
from blog.models import Comentario
from .models import UserRestriction
from .utils import group_required
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Ajusta esto según tu template

def index(request):
    entradas = EntradaBlog.objects.select_related('autor', 'monster').order_by('-fecha_creacion')[:9]
    return render(request, 'core/index.html', {'entradas': entradas})

def small_monsters(request):
    entradas = EntradaBlog.objects.filter(
        tipo='small_monster'
    ).select_related('monster', 'monster__monster_type').prefetch_related(
        'monster__elements', 'monster__ailments', 'monster__weaknesses'
    ).order_by('-fecha_creacion')
    
    paginator = Paginator(entradas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/small_monsters.html', {'page_obj': page_obj})

def custom_logout(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'¡Hasta pronto, {username}! Esperamos verte de nuevo en la cacería.')
    return redirect('core:index')

def large_monsters(request):
    entradas = EntradaBlog.objects.filter(
        tipo='large_monster'
    ).select_related(
        'monster', 
        'monster__monster_type'
    ).prefetch_related(
        'monster__elements',
        'monster__ailments',
        'monster__weaknesses'
    ).order_by('-fecha_creacion')
    
    paginator = Paginator(entradas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/large_monsters.html', {'page_obj': page_obj})

def elder_dragons(request):
    entradas = EntradaBlog.objects.filter(
        tipo='elder_dragon'
    ).select_related(
        'monster', 
        'monster__monster_type'
    ).prefetch_related(
        'monster__elements',
        'monster__ailments',
        'monster__weaknesses'
    ).order_by('-fecha_creacion')
    
    paginator = Paginator(entradas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/elder_dragons.html', {'page_obj': page_obj})

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    
    # Obtener estadísticas
    stats = {
        'total_posts': EntradaBlog.objects.filter(autor=user).count(),
        'total_comments': Comentario.objects.filter(autor=user).count(),
        'join_date': user.date_joined,
    }
    
    # Obtener posts y comentarios recientes con paginación
    posts = EntradaBlog.objects.filter(autor=user).select_related('monster').order_by('-fecha_creacion')
    comments = Comentario.objects.filter(autor=user).select_related('entrada').order_by('-fecha')
    
    # Paginación inicial (5 elementos por página)
    posts_page = request.GET.get('posts_page', 1)
    comments_page = request.GET.get('comments_page', 1)
    
    posts_paginator = Paginator(posts, 5)
    comments_paginator = Paginator(comments, 5)
    
    try:
        posts = posts_paginator.page(posts_page)
        comments = comments_paginator.page(comments_page)
    except (EmptyPage, InvalidPage):
        posts = posts_paginator.page(1)
        comments = comments_paginator.page(1)
    
    # Obtener restricciones activas
    active_restrictions = UserRestriction.objects.filter(
        user=user,
        end_date__gt=timezone.now()
    ).select_related('restricted_by')
    
    # Verificar si el usuario actual es moderador o admin
    can_restrict = request.user.groups.filter(name='Moderators').exists() or request.user.is_superuser
    is_own_profile = request.user == user
    
    context = {
        'profile_user': user,
        'stats': stats,
        'posts': posts,
        'comments': comments,
        'active_restrictions': active_restrictions,
        'can_restrict': can_restrict,
        'is_own_profile': is_own_profile,
    }
    
    # Si es una petición AJAX, devolver solo el contenido nuevo
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        content_type = request.GET.get('content_type')
        ajax_context = {
            'is_own_profile': is_own_profile,
            'can_restrict': can_restrict,
        }
        
        try:
            if content_type == 'posts':
                if posts.has_next():
                    ajax_context['posts'] = posts
                    return render(request, 'core/partials/post_cards.html', ajax_context)
                return HttpResponse('')
            elif content_type == 'comments':
                if comments.has_next():
                    ajax_context['comments'] = comments
                    return render(request, 'core/partials/comment_cards.html', ajax_context)
                return HttpResponse('')
        except (EmptyPage, InvalidPage):
            return HttpResponse('')
    
    return render(request, 'core/user_profile.html', context)

def setup_groups():
    # Crear grupos si no existen
    usuarios_group, _ = Group.objects.get_or_create(name='Usuarios')
    moderators_group, _ = Group.objects.get_or_create(name='Moderators')
    
    # Obtener los content types para los modelos
    blog_content_type = ContentType.objects.get_for_model(EntradaBlog)
    comment_content_type = ContentType.objects.get_for_model(Comentario)
    
    # Permisos para usuarios normales (solo crear y editar sus propios contenidos)
    usuarios_permissions = [
        Permission.objects.get(codename='add_entradablog', content_type=blog_content_type),
        Permission.objects.get(codename='add_comentario', content_type=comment_content_type),
    ]
    
    # Permisos para moderadores (pueden gestionar todo el contenido)
    moderator_permissions = Permission.objects.filter(
        content_type__in=[blog_content_type, comment_content_type]
    )
    
    # Asignar permisos a los grupos
    usuarios_group.permissions.set(usuarios_permissions)
    moderators_group.permissions.set(moderator_permissions)
    
    return {
        'usuarios': usuarios_group,
        'moderators': moderators_group
    }

@login_required
def restrict_user(request, username):
    # Verificar si el usuario es moderador o admin
    if not (request.user.groups.filter(name='Moderators').exists() or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para restringir usuarios.')
        return redirect('core:index')
    
    user = get_object_or_404(User, username=username)
    
    # Verificar que el moderador no pueda restringir a otros moderadores o admins
    if request.user.groups.filter(name='Moderators').exists() and (
        user.groups.filter(name='Moderators').exists() or user.is_superuser
    ):
        messages.error(request, 'No tienes permiso para restringir a moderadores o administradores.')
        return redirect('core:user_profile', username=username)
    
    if request.method == 'POST':
        restriction_type = request.POST.get('restriction_type')
        duration_days = int(request.POST.get('duration_days'))
        reason = request.POST.get('reason')
        
        if restriction_type and duration_days and reason:
            UserRestriction.objects.create(
                user=user,
                restricted_by=request.user,
                restriction_type=restriction_type,
                duration_days=duration_days,
                reason=reason
            )
            messages.success(request, f'Restricción aplicada a {username} exitosamente.')
        else:
            messages.error(request, 'Por favor completa todos los campos.')
            
    return redirect('core:user_profile', username=username)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(EntradaBlog, id=post_id)
    
    # Admin puede borrar cualquier post
    if request.user.is_superuser:
        post.delete()
        messages.success(request, 'Post eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Moderador puede borrar posts de usuarios normales
    if request.user.groups.filter(name='Moderators').exists() and not (
        post.autor.groups.filter(name='Moderators').exists() or post.autor.is_superuser
    ):
        post.delete()
        messages.success(request, 'Post eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Usuario normal solo puede borrar sus propios posts
    if request.user == post.autor:
        post.delete()
        messages.success(request, 'Post eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    messages.error(request, 'No tienes permiso para eliminar este post.')
    return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comentario, id=comment_id)
    
    # Admin puede borrar cualquier comentario
    if request.user.is_superuser:
        comment.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Moderador puede borrar comentarios de usuarios normales
    if request.user.groups.filter(name='Moderators').exists() and not (
        comment.autor.groups.filter(name='Moderators').exists() or comment.autor.is_superuser
    ):
        comment.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Usuario normal solo puede borrar sus propios comentarios
    if request.user == comment.autor:
        comment.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    messages.error(request, 'No tienes permiso para eliminar este comentario.')
    return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))

@login_required
def activate_konami(request):
    if request.method == 'POST':
        user = request.user
        
        # Verificar que el usuario no sea ya un moderador o admin
        if not (user.groups.filter(name='Moderators').exists() or user.is_superuser):
            # Obtener los grupos
            groups = setup_groups()
            
            # Remover del grupo de usuarios normales
            user.groups.remove(groups['usuarios'])
            
            # Agregar al grupo de moderadores
            user.groups.add(groups['moderators'])
            
            messages.success(request, '¡Felicitaciones! Ahora eres un moderador.')
        else:
            messages.warning(request, 'Ya tienes privilegios de moderador o administrador.')
            
    return redirect('core:index')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']
            
            # Enviar el correo
            subject = f'Nuevo mensaje de contacto de {nombre}'
            message = f'''
Nuevo mensaje de contacto recibido:

Nombre: {nombre}
Email: {email}

Mensaje:
{mensaje}

Este mensaje fue enviado desde el formulario de contacto de MhBlog.
'''
            from_email = settings.EMAIL_HOST_USER  # Cambiado para usar el email configurado
            recipient_list = ['yeyobitz@proton.me']
            
            try:
                # Intentar enviar el correo y capturar cualquier error
                result = send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False  # Cambiado para ver errores
                )
                
                if result == 1:
                    messages.success(request, 'Tu mensaje ha sido enviado correctamente. ¡Gracias por contactarnos!')
                else:
                    print(f"El correo no se envió correctamente. Resultado: {result}")
                    messages.error(request, 'Hubo un error al enviar el mensaje. Por favor, intenta nuevamente.')
                
            except Exception as e:
                print(f"Error detallado al enviar el correo: {str(e)}")
                messages.error(request, 'Hubo un error al enviar el mensaje. Por favor, intenta nuevamente.')
            
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})

