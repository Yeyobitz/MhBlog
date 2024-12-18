from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('small-monsters/', views.small_monsters, name='small_monsters'),
    path('large-monsters/', views.large_monsters, name='large_monsters'),
    path('elder-dragons/', views.elder_dragons, name='elder_dragons'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/restrict/', views.restrict_user, name='restrict_user'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
] 