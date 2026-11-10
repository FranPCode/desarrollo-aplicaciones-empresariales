"""Parte 2 — La CLI headless: el contrato que un script o un agente puede dar por hecho."""

import json
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from tienda.models import LineaPedido, Pedido, Producto


def tiendactl(*args):
    salida = StringIO()
    call_command('tiendactl', *args, stdout=salida)
    return salida.getvalue()


class CliTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos', stdout=StringIO())

    def test_con_json_la_salida_es_solo_json(self):
        datos = json.loads(tiendactl('stock', '--umbral', '2', '--json'))
        self.assertEqual(datos, [{'nombre': '7up 500ml', 'stock': 0}, {'nombre': 'Triángulo', 'stock': 1},
                                 {'nombre': 'Chizito', 'stock': 2}])

    def test_los_importes_viajan_como_texto_exacto(self):
        datos = json.loads(tiendactl('categoria', 'Gaseosas', '--json'))
        self.assertEqual([f['precio'] for f in datos], ['1.70', '2.50', '1.80'])

    def test_sin_json_es_texto_para_personas(self):
        self.assertIn('Ana Quispe · 2', tiendactl('clientes'))

    def test_codigo_2_si_los_argumentos_no_valen(self):
        with self.assertRaises(CommandError) as e:
            tiendactl('stock', '--umbral', '-1')
        self.assertEqual(e.exception.returncode, 2)

    def test_codigo_3_si_no_existe(self):
        with self.assertRaises(CommandError) as e:
            tiendactl('pedido', '999')
        self.assertEqual(e.exception.returncode, 3)

    def test_la_cli_nunca_escribe(self):
        antes = (Producto.objects.count(), Pedido.objects.filter(estado='anulado').count(), LineaPedido.objects.count())
        for orden in (['stock'], ['clientes'], ['ventas'], ['categoria', 'Chocolates']):
            tiendactl(*orden, '--json')
        despues = (Producto.objects.count(), Pedido.objects.filter(estado='anulado').count(), LineaPedido.objects.count())
        self.assertEqual(antes, despues)
