from django.shortcuts import render
from blog.models import EntradaBlog, Element, Ailment, Game
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect

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
    logout(request)
    return redirect('index')

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

