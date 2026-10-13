from . import views
from django.urls import path


app_name = 'encuesta'


urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pregunta_id>/', views.detalle, name='detalle'),
    path('<int:pregunta_id>/votar', views.votar, name='votar')
]
