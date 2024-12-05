# Generated by Django 5.1.2 on 2024-12-04 04:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Habitat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('clima', models.CharField(max_length=50)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='habitats/')),
            ],
            options={
                'verbose_name_plural': 'Habitats',
            },
        ),
        migrations.CreateModel(
            name='EntradaBlog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('tipo', models.CharField(choices=[('Monstruo grande', 'Monstruo grande'), ('Monstruo chico', 'Monstruo chico'), ('Flora', 'Flora')], max_length=20)),
                ('descripcion', models.TextField()),
                ('resumen', models.TextField()),
                ('imagen', models.ImageField(upload_to='imagenes/')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('autor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('habitat', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entradas', to='blog.habitat')),
            ],
            options={
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('entrada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='blog.entradablog')),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
    ]
