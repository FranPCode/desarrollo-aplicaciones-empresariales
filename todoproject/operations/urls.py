from django.urls import path
from . import views

urlpatterns = [
    path('suma/<int:a>/<int:b>', views.sum, name='suma'),
    path('resta/<int:a>/<int:b>', views.substract, name='resta'),
    path('multiplicacion/<int:a>/<int:b>', views.multiply, name='multiplicacion'),
]