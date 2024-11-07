from django.db import models

class EntradaBlog(models.Model):
    # Opciones para el tipo de entrada
    TIPO_CHOICES = [
        ('Monstruo grande', 'Monstruo grande'),
        ('Monstruo chico', 'Monstruo chico'),
        ('Flora', 'Flora'),
    ]

    # Campos del modelo
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    resumen = models.TextField()
    imagen = models.ImageField(upload_to='imagenes/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)  # Actualiza en cada modificación

    def __str__(self):
        return self.nombre
