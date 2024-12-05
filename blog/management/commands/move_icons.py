import os
import shutil
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Move monster icons to static folder'

    def handle(self, *args, **kwargs):
        source_dir = 'icons/'
        dest_dir = 'core/static/core/img/monsters/'
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        for filename in os.listdir(source_dir):
            if filename.endswith('.png'):
                shutil.copy(
                    os.path.join(source_dir, filename),
                    os.path.join(dest_dir, filename)
                )
                self.stdout.write(f'Copied {filename}') 