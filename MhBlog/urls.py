from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('blog/', include('blog.urls')),
    # Rutas de autenticación
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)