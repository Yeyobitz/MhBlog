from django.shortcuts import render
from blog.models import EntradaBlog

# Vista para la página de inicio
def index(request):
    # Obtenemos las últimas 5 entradas, ordenadas por fecha de creación
    entradas = EntradaBlog.objects.order_by('-fecha_creacion')[:5]
    return render(request, 'core/index.html', {'entradas': entradas})


# Vista para la sección de monstruos grandes
def monstruos(request):
    # Filtramos solo los monstruos grandes
    entradas = EntradaBlog.objects.filter(tipo='Monstruo grande').order_by('-fecha_creacion')
    return render(request, 'core/monstruos.html', {'entradas': entradas})

# Vista para la sección de flora
def flora(request):
    # Filtramos solo las entradas de flora
    entradas = EntradaBlog.objects.filter(tipo='Flora').order_by('-fecha_creacion')
    return render(request, 'core/flora.html', {'entradas': entradas})

# Vista para la sección de fauna (monstruos pequeños)
def fauna(request):
    # Filtramos solo los monstruos pequeños
    entradas = EntradaBlog.objects.filter(tipo='Monstruo chico').order_by('-fecha_creacion')
    return render(request, 'core/fauna.html', {'entradas': entradas})

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

