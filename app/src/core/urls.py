from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from . import views

urlpatterns = [
    path(route="admin/", view=admin.site.urls),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
