from django.core.management.base import BaseCommand
from blog.models import Monster, EntradaBlog
from django.contrib.auth.models import User
from django.core.files import File
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = 'Create blog entries for monsters'

    def handle(self, *args, **kwargs):
        # Crear directorio media/monsters si no existe
        media_monsters_dir = os.path.join(settings.MEDIA_ROOT, 'monsters')
        if not os.path.exists(media_monsters_dir):
            os.makedirs(media_monsters_dir)

        # Obtener o crear un usuario admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )

        # Crear entradas para cada monstruo
        for monster in Monster.objects.all():
            # Determinar el tipo basado en el monster_type y is_large
            if monster.monster_type.name == "Elder Dragon":
                tipo = 'elder_dragon'
            elif monster.is_large:
                tipo = 'large_monster'
            else:
                tipo = 'small_monster'
            
            # Obtener la info del juego más reciente
            game_info = monster.game_info.first()
            
            if game_info and game_info.image:
                # Ruta de origen (static)
                source_path = os.path.join(settings.STATIC_ROOT, 'core/img/monsters', game_info.image)
                # Ruta de destino (media)
                dest_path = os.path.join(media_monsters_dir, game_info.image)
                
                # Copiar imagen si existe
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    imagen_path = f"monsters/{game_info.image}"
                else:
                    imagen_path = "monsters/default.png"
            else:
                imagen_path = "monsters/default.png"

            EntradaBlog.objects.get_or_create(
                nombre=monster.name,
                defaults={
                    'tipo': tipo,
                    'descripcion': game_info.info if game_info else '',
                    'resumen': f"Información sobre {monster.name}",
                    'autor': admin_user,
                    'monster': monster,
                    'imagen': imagen_path
                }
            )
            
            self.stdout.write(f'Created entry for {monster.name}') 