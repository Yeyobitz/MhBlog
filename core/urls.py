from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('small-monsters/', views.small_monsters, name='small_monsters'),
    path('large-monsters/', views.large_monsters, name='large_monsters'),
    path('elder-dragons/', views.elder_dragons, name='elder_dragons'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('restrict_user/<int:user_id>/', views.restrict_user, name='restrict_user'),
    path('contact/', views.contact, name='contact'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('activate-konami/', views.activate_konami, name='activate_konami'),
] 