from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from blog import views as blog_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.index, name='index'),
    path('monstruos/', core_views.monstruos, name='monstruos'),
    path('flora/', core_views.flora, name='flora'),
    path('fauna/', core_views.fauna, name='fauna'),
    path('entrada/<int:id>/', blog_views.detalle_entrada, name='detalle_entrada'),
    path('blog/', include('blog.urls')),
    path('load-more-entries/', core_views.load_more_entries, name='load_more_entries'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
