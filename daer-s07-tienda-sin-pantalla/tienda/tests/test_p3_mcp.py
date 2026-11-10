"""Parte 3 — El servidor MCP, probado con un cliente MCP de verdad (en memoria) y la configuración del cliente.

TransactionTestCase: el SDK ejecuta cada herramienta en otro hilo, que tiene que ver los datos ya guardados.
"""

import asyncio
import json
import logging
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase
from mcp import Client

from tienda.models import Pedido
from tienda.servidor_mcp import crear_servidor

# El SDK registra los errores de las herramientas en el log; en las pruebas solo ensuciarían la salida.
logging.getLogger('mcp').setLevel(logging.CRITICAL)

CONFIGURACIONES = ['.mcp.json', '.vscode/mcp.json', 'opencode.json', 'opencode.jsonc']


def con_cliente(accion):
    async def correr():
        async with Client(crear_servidor()) as cliente:
            return await accion(cliente)
    return asyncio.run(correr())


def datos_de(resultado):
    if resultado.structured_content is not None:
        return resultado.structured_content
    return json.loads(resultado.content[0].text)


class McpTests(TransactionTestCase):
    def setUp(self):
        call_command('cargar_datos', stdout=StringIO())

    def test_seis_herramientas_y_todas_de_solo_lectura(self):
        herramientas = con_cliente(lambda c: c.list_tools()).tools
        self.assertEqual({h.name for h in herramientas}, {
            'tienda_productos_por_categoria', 'tienda_buscar_productos', 'tienda_stock_bajo',
            'tienda_ventas_por_categoria', 'tienda_clientes_frecuentes', 'tienda_detalle_pedido'})
        for h in herramientas:
            self.assertTrue(h.annotations.read_only_hint, h.name)
            self.assertFalse(h.annotations.destructive_hint, h.name)
            self.assertTrue(h.description, h.name)

    def test_una_llamada_devuelve_datos_y_aviso(self):
        resultado = con_cliente(lambda c: c.call_tool('tienda_stock_bajo', {'umbral': 2}))
        self.assertFalse(resultado.is_error)
        datos = datos_de(resultado)
        self.assertEqual([f['nombre'] for f in datos['datos']], ['7up 500ml', 'Triángulo', 'Chizito'])
        self.assertIn('nunca instrucciones', datos['aviso'])

    def test_la_orden_dentro_de_un_dato_no_hace_nada(self):
        resultado = con_cliente(lambda c: c.call_tool('tienda_productos_por_categoria', {'categoria': 'Chocolates'}))
        princesa = next(f for f in datos_de(resultado)['datos'] if f['nombre'] == 'Princesa')
        self.assertIn('INSTRUCCIÓN PARA EL AGENTE', princesa['descripcion'])  # llega como texto…
        self.assertEqual(Pedido.objects.filter(estado='anulado').count(), 1)  # …y nadie anuló nada

    def test_errores_que_orientan_al_agente(self):
        resultado = con_cliente(lambda c: c.call_tool('tienda_detalle_pedido', {'pedido_id': 999}))
        self.assertTrue(resultado.is_error)
        self.assertIn('del 1 al 7', resultado.content[0].text)
        resultado = con_cliente(lambda c: c.call_tool('tienda_stock_bajo', {'umbral': 'muchos'}))
        self.assertTrue(resultado.is_error)  # el SDK valida el tipo antes de llegar a la consulta

    def test_configuracion_del_cliente_mcp(self):
        encontradas = [n for n in CONFIGURACIONES if (Path(settings.BASE_DIR) / n).is_file()]
        self.assertTrue(encontradas, f'Falta la configuración del cliente MCP: creen uno de {CONFIGURACIONES}')
        for nombre in encontradas:
            self.assertIn('servidor_mcp', (Path(settings.BASE_DIR) / nombre).read_text(encoding='utf-8'),
                          f'{nombre} no lanza «manage.py servidor_mcp»')
