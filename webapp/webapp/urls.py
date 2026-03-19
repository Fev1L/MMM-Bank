from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('credits/', include('credits.urls')), 
    path('deposits/', include('deposits.urls')),
    path('more/', include('more.urls'))
]
