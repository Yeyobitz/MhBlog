from django.contrib import admin
from .models import (
    EntradaBlog, 
    Comentario,
    Game,
    Element,
    Ailment,
    MonsterType,
    Monster,
    MonsterGameInfo
)

@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    list_display = ('name', 'monster_type', 'is_large')
    list_filter = ('monster_type', 'is_large', 'elements', 'ailments')
    search_fields = ('name',)
    filter_horizontal = ('elements', 'ailments', 'weaknesses', 'subspecies')

@admin.register(MonsterGameInfo)
class MonsterGameInfoAdmin(admin.ModelAdmin):
    list_display = ('monster', 'game', 'danger')
    list_filter = ('game', 'danger')
    search_fields = ('monster__name', 'game__name')

@admin.register(EntradaBlog)
class EntradaBlogAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'autor', 'fecha_creacion')
    list_filter = ('tipo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    raw_id_fields = ('monster',)

admin.site.register(Game)
admin.site.register(Element)
admin.site.register(Ailment)
admin.site.register(MonsterType)
admin.site.register(Comentario)
