from django.db import models
from django.contrib.auth.models import User

class EntradaBlog(models.Model):
    TIPO_CHOICES = [
        ('small_monster', 'Monstruo Pequeño'),
        ('large_monster', 'Monstruo Grande'),
        ('elder_dragon', 'Dragón Anciano'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    resumen = models.TextField(help_text="Breve descripción que aparecerá en las listas")
    imagen = models.ImageField(upload_to='imagenes/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    monster = models.ForeignKey('Monster', on_delete=models.CASCADE, related_name='entradas')
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
    
    def __str__(self):
        return self.nombre

class Game(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Element(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Ailment(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class MonsterType(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Monster(models.Model):
    name = models.CharField(max_length=100)
    monster_type = models.ForeignKey(MonsterType, on_delete=models.PROTECT)
    is_large = models.BooleanField(default=True)
    elements = models.ManyToManyField(Element, blank=True)
    ailments = models.ManyToManyField(Ailment, blank=True)
    weaknesses = models.ManyToManyField(Element, related_name='weak_monsters', blank=True)
    subspecies = models.ManyToManyField('self', blank=True, symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Monstruo"
        verbose_name_plural = "Monstruos"

class MonsterGameInfo(models.Model):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE, related_name='game_info')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    image = models.CharField(max_length=200)
    info = models.TextField()
    danger = models.IntegerField(null=True, blank=True)
    
    class Meta:
        unique_together = ['monster', 'game']

    def __str__(self):
        return f"{self.monster.name} - {self.game.name}"

class Comentario(models.Model):
    entrada = models.ForeignKey(EntradaBlog, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Comentario de {self.autor} en {self.entrada}'
