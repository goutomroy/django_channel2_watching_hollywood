from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from main.views import MainViewSet

router = DefaultRouter()
router.register(r'main', MainViewSet, base_name='main')

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)