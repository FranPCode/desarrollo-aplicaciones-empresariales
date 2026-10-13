
from django.urls import include, path
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]


urlpatterns = [
    path('encuesta/', include('encuesta.urls')),
    path('admin/', admin.site.urls),
]
