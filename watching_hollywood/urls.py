from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
