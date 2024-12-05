from django.core.management.base import BaseCommand
import json
from blog.models import Monster, MonsterType, Element, Ailment, Game, MonsterGameInfo

class Command(BaseCommand):
    help = 'Import monsters from JSON file'

    def handle(self, *args, **kwargs):
        # Cambiar la codificación a utf-8
        with open('monsters.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Limpiar datos existentes
        self.stdout.write('Limpiando datos existentes...')
        MonsterGameInfo.objects.all().delete()
        Monster.objects.all().delete()
        MonsterType.objects.all().delete()
        Element.objects.all().delete()
        Ailment.objects.all().delete()
        Game.objects.all().delete()
            
        # Crear tipos, elementos y ailments únicos
        monster_types = set()
        elements = set()
        ailments = set()
        games = set()
        
        for monster in data['monsters']:
            monster_types.add(monster['type'])
            if 'elements' in monster:
                elements.update(monster['elements'])
            if 'ailments' in monster:
                ailments.update(monster['ailments'])
            if 'weakness' in monster:
                elements.update(monster['weakness'])
            for game_info in monster['games']:
                games.add(game_info['game'])
        
        # Crear registros en la base de datos
        self.stdout.write('Creando tipos de monstruos...')
        type_dict = {t: MonsterType.objects.create(name=t) for t in monster_types}
        
        self.stdout.write('Creando elementos...')
        element_dict = {e: Element.objects.create(name=e) for e in elements}
        
        self.stdout.write('Creando ailments...')
        ailment_dict = {a: Ailment.objects.create(name=a) for a in ailments}
        
        self.stdout.write('Creando juegos...')
        game_dict = {g: Game.objects.create(name=g) for g in games}
        
        # Importar monstruos
        self.stdout.write('Importando monstruos...')
        total = len(data['monsters'])
        for i, monster_data in enumerate(data['monsters'], 1):
            try:
                self.stdout.write(f'Importando monstruo {i}/{total}: {monster_data["name"]}')
                
                monster = Monster.objects.create(
                    name=monster_data['name'],
                    monster_type=type_dict[monster_data['type']],
                    is_large=monster_data.get('isLarge', True)
                )
                
                # Agregar elementos
                if 'elements' in monster_data:
                    monster.elements.add(*[element_dict[e] for e in monster_data['elements']])
                
                # Agregar ailments
                if 'ailments' in monster_data:
                    monster.ailments.add(*[ailment_dict[a] for a in monster_data['ailments']])
                
                # Agregar debilidades
                if 'weakness' in monster_data:
                    monster.weaknesses.add(*[element_dict[w] for w in monster_data['weakness']])
                
                # Agregar info de juegos
                for game_info in monster_data['games']:
                    MonsterGameInfo.objects.create(
                        monster=monster,
                        game=game_dict[game_info['game']],
                        image=game_info.get('image', ''),  # Hacer opcional
                        info=game_info.get('info', ''),    # Hacer opcional
                        danger=game_info.get('danger')     # Ya era opcional
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importando {monster_data["name"]}: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {total} monsters'))