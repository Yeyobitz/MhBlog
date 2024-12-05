from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .models import EntradaBlog, Habitat, Comentario
from .forms import ComentarioForm, EntradaBlogForm

def inicio(request):
    entradas = EntradaBlog.objects.select_related('habitat', 'autor').all()[:5]
    return render(request, 'blog/inicio.html', {'entradas': entradas})

def lista_entradas(request):
    # Obtener parámetros de filtro
    tipo = request.GET.get('tipo')
    habitat_id = request.GET.get('habitat')
    
    # Query base
    entradas = EntradaBlog.objects.select_related('habitat', 'autor').all()
    
    # Aplicar filtros
    if tipo:
        entradas = entradas.filter(tipo=tipo)
    if habitat_id:
        entradas = entradas.filter(habitat_id=habitat_id)
    
    # Paginación
    paginator = Paginator(entradas, 9)  # 9 entradas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener habitats para el formulario de filtro
    habitats = Habitat.objects.all()
    
    context = {
        'page_obj': page_obj,
        'habitats': habitats,
        'tipo_actual': tipo,
        'habitat_actual': habitat_id,
        'tipos': EntradaBlog.TIPO_CHOICES
    }
    
    return render(request, 'blog/lista_entradas.html', context)

def detalle_entrada(request, id):
    entrada = get_object_or_404(EntradaBlog.objects.select_related('habitat', 'autor'), id=id)
    comentarios = entrada.comentarios.select_related('autor').all()
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.entrada = entrada
            comentario.autor = request.user
            comentario.save()
            messages.success(request, '¡Comentario agregado!')
            return redirect('blog:detalle_entrada', id=id)
    else:
        form = ComentarioForm()
    
    context = {
        'entrada': entrada,
        'comentarios': comentarios,
        'form': form
    }
    return render(request, 'blog/detalle_entrada.html', context)

@login_required
def crear_entrada(request):
    if request.method == 'POST':
        form = EntradaBlogForm(request.POST, request.FILES)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.autor = request.user
            entrada.save()
            messages.success(request, '¡Entrada creada exitosamente!')
            return redirect('blog:detalle_entrada', id=entrada.id)
    else:
        form = EntradaBlogForm()
    
    return render(request, 'blog/crear_entrada.html', {'form': form})

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
        field.widget.attrs['placeholder'] = field.label
    
    return render(request, 'core/registro.html', {'form': form})

def login_view(request):
    # Tu lógica de login aquí
    return render(request, 'core/login.html')