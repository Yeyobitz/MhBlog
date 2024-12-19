from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import EntradaBlog, Comentario

class Command(BaseCommand):
    help = 'Configura los grupos y permisos iniciales'

    def handle(self, *args, **kwargs):
        # Crear grupos si no existen
        usuarios_group, created = Group.objects.get_or_create(name='Usuarios')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Usuarios" creado'))
        
        moderators_group, created = Group.objects.get_or_create(name='Moderators')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Moderators" creado'))
        
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
        self.stdout.write(self.style.SUCCESS('Permisos asignados al grupo "Usuarios"'))
        
        moderators_group.permissions.set(moderator_permissions)
        self.stdout.write(self.style.SUCCESS('Permisos asignados al grupo "Moderators"')) 