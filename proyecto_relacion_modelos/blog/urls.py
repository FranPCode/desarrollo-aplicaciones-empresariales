from . import views
from django.urls import path


urlpatterns = [
    path('entradas/', views.lista_entradas, name='lista_entradas'),
    path(
        'entradas/autor/<int:autor_id>/',
        views.entradas_por_autor,
        name='entradas_por_autor',
    ),
]
