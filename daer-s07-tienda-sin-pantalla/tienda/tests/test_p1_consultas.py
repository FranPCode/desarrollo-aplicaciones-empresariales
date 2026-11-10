"""Parte 1 — Las seis consultas del ORM. NO editen las pruebas: son el oráculo del laboratorio."""

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from tienda.models import Pedido
from tienda.version import modulo


class ConsultasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos', stdout=StringIO())

    @property
    def c(self):
        return modulo('consultas')

    def test_productos_por_categoria(self):
        for nombre in ('Gaseosas', 'gaseosas', 'GASEOSAS'):
            filas = self.c.productos_por_categoria(nombre)
            self.assertEqual([f['nombre'] for f in filas], ['7up 500ml', 'Coca Cola 500ml', 'Fanta 500ml'], nombre)
        self.assertEqual(filas[2]['precio'], Decimal('1.80'))
        self.assertEqual(filas[2]['descripcion'], 'Gaseosa de naranja.')
        self.assertEqual(self.c.productos_por_categoria('Helados'), [])

    def test_buscar_productos_en_nombre_o_descripcion(self):
        self.assertEqual(self.c.buscar_productos('chocolate'), ['Picaras', 'Princesa', 'Sublime', 'Triángulo'])
        self.assertEqual(self.c.buscar_productos('FANTA'), ['Fanta 500ml'])
        self.assertEqual(self.c.buscar_productos('zzz'), [])

    def test_stock_bajo(self):
        self.assertEqual(self.c.stock_bajo(), [
            {'nombre': '7up 500ml', 'stock': 0}, {'nombre': 'Triángulo', 'stock': 1},
            {'nombre': 'Chizito', 'stock': 2}, {'nombre': 'Coronita Fresa', 'stock': 3},
            {'nombre': 'Coca Cola 500ml', 'stock': 4}])
        self.assertEqual([f['nombre'] for f in self.c.stock_bajo(0)], ['7up 500ml'])

    def test_ventas_por_categoria_solo_pagadas(self):
        self.assertEqual(self.c.ventas_por_categoria(), [
            {'categoria': 'Chocolates', 'total': Decimal('8.40')},
            {'categoria': 'Gaseosas', 'total': Decimal('7.90')},
            {'categoria': 'Galletas', 'total': Decimal('4.00')},
            {'categoria': 'Snacks', 'total': Decimal('2.00')}])

    def test_clientes_frecuentes(self):
        self.assertEqual(self.c.clientes_frecuentes(), [
            {'nombre': 'Ana Quispe', 'pedidos_pagados': 2}, {'nombre': 'Luis Torres', 'pedidos_pagados': 2}])
        self.assertEqual([f['nombre'] for f in self.c.clientes_frecuentes(1)],
                         ['Ana Quispe', 'Luis Torres', 'María Rojas'])

    def test_detalle_de_un_pedido(self):
        primero = Pedido.objects.get(cliente__nombre='Ana Quispe', fecha__day=3)
        datos = self.c.detalle_pedido(primero.pk)
        self.assertEqual((datos['pedido'], datos['cliente'], datos['estado']), (primero.pk, 'Ana Quispe', 'pagado'))
        self.assertEqual(datos['lineas'], [
            {'producto': 'Fanta 500ml', 'cantidad': 2, 'precio_unitario': Decimal('1.80'), 'subtotal': Decimal('3.60')},
            {'producto': 'Picaras', 'cantidad': 3, 'precio_unitario': Decimal('1.00'), 'subtotal': Decimal('3.00')}])
        self.assertEqual(datos['total'], Decimal('6.60'))

    def test_detalle_de_un_pedido_en_dos_consultas(self):
        pedido = Pedido.objects.get(cliente__nombre='María Rojas')
        with self.assertNumQueries(2):
            self.c.detalle_pedido(pedido.pk)

    def test_pedido_inexistente(self):
        self.assertIsNone(self.c.detalle_pedido(999))
