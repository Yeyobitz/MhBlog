from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('detalle/<int:id>/', views.detalle_entrada, name='detalle_entrada'),
]
