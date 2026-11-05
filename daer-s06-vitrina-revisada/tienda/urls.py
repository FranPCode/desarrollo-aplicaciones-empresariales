from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('producto/<int:producto_id>/', views.producto, name='producto'),
    path('categoria/<int:categoria_id>/', views.categoria, name='categoria'),
]
