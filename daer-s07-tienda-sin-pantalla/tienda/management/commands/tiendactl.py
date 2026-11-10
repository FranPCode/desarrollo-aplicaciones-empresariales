"""La tienda sin pantalla: una CLI para personas, scripts y agentes. Ya está hecha (Parte 2).

    python manage.py tiendactl categoria Gaseosas
    python manage.py tiendactl buscar chocolate --json
    python manage.py tiendactl stock --umbral 5
    python manage.py tiendactl ventas
    python manage.py tiendactl clientes --minimo 2
    python manage.py tiendactl pedido 3 --json

Contrato «headless» (lo que un programa puede dar por hecho):
- con --json la salida es SOLO JSON válido, sin adornos; sin --json es texto para leer;
- código de salida 0 = bien (aunque la lista salga vacía), 2 = argumentos inválidos, 3 = no existe;
- nunca pide nada por teclado y nunca modifica la base de datos.

Las consultas salen de la versión activa (TIENDA_VERSION; por defecto, las suyas).
"""

import argparse

from django.core.management.base import BaseCommand, CommandError

from tienda.formato import a_json, volcar
from tienda.version import modulo


class Command(BaseCommand):
    help = 'Consulta la tienda desde la terminal (solo lectura).'
    requires_system_checks = []

    def add_arguments(self, parser):
        comun = argparse.ArgumentParser(add_help=False)
        comun.add_argument('--json', action='store_true', help='salida en JSON (para scripts y agentes)')
        sub = parser.add_subparsers(dest='orden', required=True, parser_class=type(parser))
        orden = lambda nombre, ayuda: sub.add_parser(nombre, help=ayuda, parents=[comun], called_from_command_line=False)  # noqa: E731
        orden('categoria', 'productos de una categoría').add_argument('nombre')
        orden('buscar', 'productos cuyo nombre o descripción contiene un texto').add_argument('texto')
        orden('stock', 'productos con poco stock').add_argument('--umbral', type=int, default=5)
        orden('ventas', 'ventas pagadas por categoría')
        orden('clientes', 'clientes con varios pedidos pagados').add_argument('--minimo', type=int, default=2)
        orden('pedido', 'detalle de un pedido').add_argument('id', type=int)

    def handle(self, *args, orden, json, **opciones):
        c = modulo('consultas')
        if orden == 'categoria':
            datos = c.productos_por_categoria(opciones['nombre'])
        elif orden == 'buscar':
            datos = c.buscar_productos(opciones['texto'])
        elif orden == 'stock':
            if opciones['umbral'] < 0:
                raise CommandError('--umbral no puede ser negativo', returncode=2)
            datos = c.stock_bajo(opciones['umbral'])
        elif orden == 'ventas':
            datos = c.ventas_por_categoria()
        elif orden == 'clientes':
            if opciones['minimo'] < 1:
                raise CommandError('--minimo tiene que ser 1 o más', returncode=2)
            datos = c.clientes_frecuentes(opciones['minimo'])
        else:
            datos = c.detalle_pedido(opciones['id'])
            if datos is None:
                raise CommandError(f'No existe el pedido {opciones["id"]}', returncode=3)

        self.stdout.write(volcar(datos) if json else self.texto(a_json(datos)))

    def texto(self, datos):
        if isinstance(datos, dict):  # el detalle de un pedido
            lineas = [f'Pedido {datos["pedido"]} de {datos["cliente"]} ({datos["estado"]})']
            lineas += [f'  {li["cantidad"]} × {li["producto"]} a S/ {li["precio_unitario"]} = S/ {li["subtotal"]}'
                       for li in datos['lineas']]
            return '\n'.join(lineas + [f'  Total: S/ {datos["total"]}'])
        if not datos:
            return '(sin resultados)'
        if isinstance(datos[0], dict):
            return '\n'.join(' · '.join(str(v) for v in fila.values()) for fila in datos)
        return '\n'.join(str(v) for v in datos)
