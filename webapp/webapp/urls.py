from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # default, part of django
    path('', include('main.urls')),
    path('credits/', include('credits.urls')), 
    path('deposites/', include('deposites.urls')), 
    path('more/', include('more.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
