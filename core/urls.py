from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('monstruos/', views.monstruos, name='monstruos'),
    path('flora/', views.flora, name='flora'),
    path('fauna/', views.fauna, name='fauna'),
] 