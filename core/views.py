from django.shortcuts import render
from blog.models import EntradaBlog, Element, Ailment, Game
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger as InvalidPage
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from blog.models import Comentario
from .models import UserRestriction
from .utils import role_required
from django.http import HttpResponse

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
    user = get_object_or_404(User.objects.select_related('profile'), username=username)
    
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
    can_restrict = request.user.profile.role in ['moderador', 'admin']
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

@login_required
def restrict_user(request, username):
    # Primero verificamos si el usuario tiene permiso para restringir
    if request.user.profile.role not in ['moderador', 'admin']:
        messages.error(request, 'No tienes permisos para restringir usuarios.')
        return redirect('core:index')
    
    user = get_object_or_404(User, username=username)
    
    # Verificar que el moderador no pueda restringir a otros moderadores o admins
    if request.user.profile.role == 'moderador' and user.profile.role in ['moderador', 'admin']:
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
    
    # Verificar permisos según el rol
    user_role = request.user.profile.role
    
    # Admin puede borrar cualquier post
    if user_role == 'admin':
        post.delete()
        messages.success(request, 'Post eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Moderador puede borrar posts de usuarios normales
    if user_role == 'moderador' and post.autor.profile.role == 'normal':
        post.delete()
        messages.success(request, 'Post eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Usuario normal solo puede borrar sus propios posts
    if user_role == 'normal' and request.user == post.autor:
        post.delete()
        messages.success(request, 'Post eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    messages.error(request, 'No tienes permiso para eliminar este post.')
    return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comentario, id=comment_id)
    
    # Verificar permisos según el rol
    user_role = request.user.profile.role
    
    # Admin puede borrar cualquier comentario
    if user_role == 'admin':
        comment.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Moderador puede borrar comentarios de usuarios normales
    if user_role == 'moderador' and comment.autor.profile.role == 'normal':
        comment.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    # Usuario normal solo puede borrar sus propios comentarios
    if user_role == 'normal' and request.user == comment.autor:
        comment.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))
    
    messages.error(request, 'No tienes permiso para eliminar este comentario.')
    return redirect(request.META.get('HTTP_REFERER', 'core:user_profile'))

