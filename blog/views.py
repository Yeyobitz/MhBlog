from django.shortcuts import render, get_object_or_404
from .models import EntradaBlog

def inicio(request):
    entradas = EntradaBlog.objects.order_by('-fecha_creacion')[:5]  # Últimas 5 entradas
    print("Entradas en inicio:", entradas)  # Verificar entradas en consola
    return render(request, 'inicio.html', {'entradas': entradas})


def lista_entradas(request, tipo):
    entradas = EntradaBlog.objects.filter(tipo=tipo).order_by('-fecha_creacion')
    print("Entradas en lista_entradas para tipo:", tipo)
    print("Datos obtenidos:", entradas)  # Depuración
    return render(request, 'lista_entradas.html', {'entradas': entradas, 'tipo': tipo})

def detalle_entrada(request, id):
    entrada = get_object_or_404(EntradaBlog, id=id)
    
    anterior_entrada = EntradaBlog.objects.filter(id__lt=entrada.id).order_by('-id').first()
    siguiente_entrada = EntradaBlog.objects.filter(id__gt=entrada.id).order_by('id').first()
    
    context = {
        'entrada': entrada,
        'anterior_entrada': anterior_entrada,
        'siguiente_entrada': siguiente_entrada,
    }
    return render(request, 'blog/detalle_entrada.html', context)
