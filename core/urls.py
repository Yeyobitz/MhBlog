from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('small-monsters/', views.small_monsters, name='small_monsters'),
    path('large-monsters/', views.large_monsters, name='large_monsters'),
    path('elder-dragons/', views.elder_dragons, name='elder_dragons'),
] 