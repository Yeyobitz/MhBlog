from django.shortcuts import render
from blog.models import EntradaBlog
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.paginator import Paginator

# Vista para la página de inicio
def index(request):
    # Obtener todas las entradas ordenadas por fecha de creación (las más recientes primero)
    entradas = EntradaBlog.objects.all().order_by('-fecha_creacion')
    
    # Configurar la paginación
    paginator = Paginator(entradas, 5)  # 5 entradas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/index.html', {
        'page_obj': page_obj,
    })


# Vista para la sección de monstruos grandes
def monstruos(request):
    # Obtener todas las entradas de tipo monstruo (grande y chico)
    entradas = EntradaBlog.objects.filter(
        tipo__in=['Monstruo grande', 'Monstruo chico']
    ).order_by('-fecha_creacion')
    
    print("Número de entradas encontradas:", entradas.count())  # Debug
    print("Tipos de entradas:", entradas.values_list('tipo', flat=True))  # Debug
    
    # Configurar paginación
    paginator = Paginator(entradas, 5)  # 5 entradas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'debug_empty': not entradas.exists(),  # Debug
    }
    return render(request, 'core/monstruos.html', context)

# Vista para la sección de flora
def flora(request):
    entradas = EntradaBlog.objects.filter(
        tipo='Flora'
    ).order_by('-fecha_creacion')
    
    paginator = Paginator(entradas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/flora.html', {
        'page_obj': page_obj
    })

# Vista para la sección de fauna (monstruos pequeños)
def fauna(request):
    # Para fauna, asumiremos que son monstruos chicos
    entradas = EntradaBlog.objects.filter(
        tipo='Monstruo chico'
    ).order_by('-fecha_creacion')
    
    paginator = Paginator(entradas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/fauna.html', {
        'page_obj': page_obj
    })

from django.http import JsonResponse
from django.core.paginator import Paginator

def load_more_entries(request):
    page_number = int(request.GET.get('page', 1))
    tipo = request.GET.get('tipo')
    
    if tipo:
        entries = EntradaBlog.objects.filter(tipo=tipo).order_by('-fecha_creacion')
    else:
        entries = EntradaBlog.objects.all().order_by('-fecha_creacion')
        
    total_entries = entries.count()
    paginator = Paginator(entries, 5)
    page_obj = paginator.get_page(page_number)
    
    data = {
        'entries': [{
            'id': entry.id,
            'nombre': entry.nombre,
            'resumen': entry.resumen,
            'imagen': entry.imagen.url,
            'fecha_creacion': entry.fecha_creacion.strftime('%Y-%m-%d')
        } for entry in page_obj],
        'has_more': page_obj.has_next() and (page_number * 5) < total_entries
    }
    return JsonResponse(data)

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
        return form


def custom_logout(request):
    logout(request)
    return redirect('index')

