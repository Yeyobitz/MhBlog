from django.db import models
from django.contrib.auth.models import User

class Habitat(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    clima = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='habitats/', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Habitats"
    
    def __str__(self):
        return self.nombre

class EntradaBlog(models.Model):
    TIPO_CHOICES = [
        ('Monstruo grande', 'Monstruo grande'),
        ('Monstruo chico', 'Monstruo chico'),
        ('Flora', 'Flora'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    resumen = models.TextField()
    imagen = models.ImageField(upload_to='imagenes/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    habitat = models.ForeignKey(Habitat, on_delete=models.SET_NULL, null=True, related_name='entradas')
    autor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre

class Comentario(models.Model):
    entrada = models.ForeignKey(EntradaBlog, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f'Comentario de {self.autor.username} en {self.entrada.nombre}'
