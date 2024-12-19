from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .models import EntradaBlog, Comentario, Element, Ailment, Game, MonsterGameInfo, Monster, MonsterType
from .forms import ComentarioForm, EntradaBlogForm
from core.forms import RegistroForm
from core.utils import group_required

def inicio(request):
    entradas = EntradaBlog.objects.select_related('habitat', 'autor').all()[:5]
    return render(request, 'blog/inicio.html', {'entradas': entradas})

def lista_entradas(request):
    queryset = EntradaBlog.objects.all()
    
    # Búsqueda por nombre
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(nombre__icontains=search)
    
    # Filtro por tipo
    tipo = request.GET.get('tipo')
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    
    # Ordenamiento
    order = request.GET.get('order', '-fecha_creacion')
    queryset = queryset.order_by(order)
    
    # Filtro por elemento
    element = request.GET.get('element')
    if element:
        queryset = queryset.filter(monster__elements__id=element)
    
    # Filtro por estado
    ailment = request.GET.get('ailment')
    if ailment:
        queryset = queryset.filter(monster__ailments__id=ailment)
    
    # Filtro por inicial
    inicial = request.GET.get('inicial')
    if inicial:
        queryset = queryset.filter(nombre__istartswith=inicial)
    
    # Filtro por peligrosidad
    danger = request.GET.get('danger')
    if danger:
        queryset = queryset.filter(monster__game_info__danger=danger)
    
    # Filtro por juego
    game = request.GET.get('game')
    if game:
        queryset = queryset.filter(monster__game_info__game__id=game)
    
    # Paginación
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener datos para los filtros
    context = {
        'page_obj': page_obj,
        'tipos': EntradaBlog.TIPO_CHOICES,
        'tipo_actual': tipo,
        'order': order,
        'elements': Element.objects.all(),
        'selected_element': element,
        'ailments': Ailment.objects.all(),
        'selected_ailment': ailment,
        'inicial': inicial,
        'danger': danger,
        'games': Game.objects.all(),
        'selected_game': game,
    }
    
    return render(request, 'blog/lista_entradas.html', context)

def detalle_entrada(request, id):
    entrada = get_object_or_404(
        EntradaBlog.objects.select_related(
            'monster', 
            'monster__monster_type', 
            'autor'
        ).prefetch_related(
            'monster__elements',
            'monster__ailments',
            'monster__weaknesses',
            'monster__game_info',
            'monster__game_info__game',
            'comentarios',
            'comentarios__autor'
        ),
        id=id
    )
    comentarios = entrada.comentarios.select_related('autor').all()
    
    if request.method == 'POST' and request.user.is_authenticated:
        # Verificar permiso para comentar
        if not request.user.has_perm('blog.add_comentario'):
            messages.error(request, 'No tienes permiso para agregar comentarios.')
            return redirect('blog:detalle_entrada', id=id)
            
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
        'form': form,
        'can_comment': request.user.is_authenticated and request.user.has_perm('blog.add_comentario')
    }
    return render(request, 'blog/detalle_entrada.html', context)

@login_required
@group_required(['Usuarios', 'Moderators'])
def crear_entrada(request):
    if request.method == 'POST':
        form = EntradaBlogForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Primero creamos el monstruo base
                monster_type = MonsterType.objects.get(name={
                    'small_monster': 'Small Monster',
                    'large_monster': 'Large Monster',
                    'elder_dragon': 'Elder Dragon'
                }[form.cleaned_data['tipo']])
                
                monster = Monster.objects.create(
                    name=form.cleaned_data['nombre'],
                    monster_type=monster_type,
                    is_large=form.cleaned_data['tipo'] != 'small_monster'
                )

                # Actualizamos los elementos, estados y debilidades del monstruo
                monster.elements.set(form.cleaned_data.get('elements', []))
                monster.ailments.set(form.cleaned_data.get('ailments', []))
                monster.weaknesses.set(form.cleaned_data.get('weaknesses', []))
                monster.save()

                # Ahora creamos la entrada
                entrada = form.save(commit=False)
                entrada.autor = request.user
                entrada.monster = monster
                entrada.save()

                # Creamos la información del juego
                MonsterGameInfo.objects.create(
                    monster=monster,
                    game=form.cleaned_data['game'],
                    danger=form.cleaned_data['danger_level'],
                    info=entrada.descripcion,
                    image=''
                )

                messages.success(request, f'''
                    ¡Felicitaciones, cazador! 🎉
                    Has contribuido exitosamente con información sobre {entrada.nombre}.
                    Tu aporte ayudará a otros cazadores en sus futuras cacerías.
                    ¡Gracias por colaborar con la comunidad! 🏹
                ''')
                return redirect('blog:detalle_entrada', id=entrada.id)
            except Exception as e:
                messages.error(request, f'Error al crear la entrada: {str(e)}')
        else:
            messages.error(request, 'Por favor verifica los datos ingresados y vuelve a intentarlo.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f'Error en {field}: {error}')
    else:
        form = EntradaBlogForm()
    
    context = {
        'form': form,
        'title': 'Crear Nueva Entrada',
    }
    return render(request, 'blog/crear_entrada.html', context)

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('login')
    else:
        form = RegistroForm()
    
    # Agregar clases de Bootstrap a los campos del formulario
    for field in form.fields.values():
        if field.widget.__class__.__name__ != 'HiddenInput':
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
    
    return render(request, 'registration/registro.html', {'form': form})

def login_view(request):
    return render(request, 'core/login.html')

@login_required
@group_required(['Usuarios', 'Moderators'])
def agregar_comentario(request, entrada_id):
    if request.method == 'POST':
        entrada = get_object_or_404(EntradaBlog, id=entrada_id)
        contenido = request.POST.get('contenido')
        
        if contenido:
            Comentario.objects.create(
                entrada=entrada,
                autor=request.user,
                contenido=contenido
            )
            messages.success(request, 'Comentario agregado exitosamente.')
            return redirect('blog:detalle_entrada', id=entrada_id)
        
    messages.error(request, 'El comentario no puede estar vacío.')
    return redirect('blog:detalle_entrada', id=entrada_id)

def index(request):
    # Obtener las 9 entradas más recientes
    entradas = EntradaBlog.objects.select_related(
        'autor', 
        'monster',
        'monster__monster_type'
    ).prefetch_related(
        'monster__elements',
        'monster__ailments',
        'monster__weaknesses'
    ).order_by('-fecha_creacion')[:9]  # Limitamos a 9 entradas
    
    return render(request, 'core/index.html', {
        'entradas': entradas,
        'show_pagination': False  # Para indicar que no queremos paginación en el index
    })

@login_required
def delete_post(request, post_id):
    if not request.user.has_perm('blog.delete_entradablog'):
        messages.error(request, 'No tienes permiso para eliminar entradas.')
        return redirect('core:index')
        
    post = get_object_or_404(EntradaBlog, id=post_id)
    
    # Solo el autor o un admin puede eliminar el post
    if request.user == post.autor or request.user.is_superuser:
        post.delete()
        messages.success(request, 'Post eliminado exitosamente.')
    else:
        messages.error(request, 'No tienes permiso para eliminar este post.')
    
    return redirect(request.META.get('HTTP_REFERER', 'core:index'))