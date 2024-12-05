from django.contrib import admin
from .models import EntradaBlog, Habitat, Comentario

@admin.register(Habitat)
class HabitatAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'clima']
    search_fields = ['nombre']

@admin.register(EntradaBlog)
class EntradaBlogAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'habitat', 'autor', 'fecha_creacion']
    list_filter = ['tipo', 'habitat', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    date_hierarchy = 'fecha_creacion'

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['autor', 'entrada', 'fecha']
    list_filter = ['fecha', 'entrada']
    search_fields = ['contenido', 'autor__username']
