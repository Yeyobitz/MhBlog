from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('entradas/', views.lista_entradas, name='lista_entradas'),
    path('entrada/<int:id>/', views.detalle_entrada, name='detalle_entrada'),
    path('crear/', views.crear_entrada, name='crear_entrada'),
    path('registro/', views.registro, name='registro'),
]