from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import home


urlpatterns = [
    path('', home),
    path('zoom-attendance/', include('zar.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', include('authenticate_ea.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
