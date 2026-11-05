"""Datos comunes de las pruebas. NO editen las pruebas: son el oráculo del laboratorio."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from tienda.models import Categoria, Producto


class VitrinaTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos', stdout=StringIO())

    def get(self, nombre, *args):
        return self.client.get(reverse(nombre, args=args))

    def producto(self, nombre):
        return Producto.objects.get(nombre=nombre)

    def categoria(self, nombre):
        return Categoria.objects.get(nombre=nombre)

    def detalle(self, nombre):
        return self.get('producto', self.producto(nombre).id)
