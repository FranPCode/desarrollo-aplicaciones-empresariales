"""Genera un reporte Markdown a partir de la CLI de la tienda."""

import json
import os
from pathlib import Path
import subprocess
import sys


PROYECTO = Path(__file__).resolve().parent.parent
REPORTE = PROYECTO / 'reporte.md'


def consultar(*argumentos):
    comando = [sys.executable, str(PROYECTO / 'manage.py'), 'tiendactl', *argumentos, '--json']
    resultado = subprocess.run(
        comando, cwd=PROYECTO, capture_output=True, text=True, encoding='utf-8',
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
    )
    if resultado.returncode != 0:
        detalle = resultado.stderr.strip() or resultado.stdout.strip()
        raise RuntimeError(
            f"tiendactl {' '.join(argumentos)} terminó con código {resultado.returncode}: {detalle}"
        )
    try:
        return json.loads(resultado.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"tiendactl {' '.join(argumentos)} no devolvió JSON válido: {error}") from error


def celda(valor):
    return str(valor).replace('\\', '\\\\').replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')


def tabla(titulos, filas):
    lineas = [
        '| ' + ' | '.join(titulos) + ' |',
        '| ' + ' | '.join('---' for _ in titulos) + ' |',
    ]
    lineas.extend('| ' + ' | '.join(celda(valor) for valor in fila) + ' |' for fila in filas)
    return '\n'.join(lineas)


def generar_reporte():
    ventas = consultar('ventas')
    stock = consultar('stock', '--umbral', '5')
    clientes = consultar('clientes', '--minimo', '2')

    return '\n\n'.join([
        '# Reporte de la tienda',
        '## Ventas por categoría\n\n' + tabla(
            ('Categoría', 'Total (S/)'),
            ((fila['categoria'], fila['total']) for fila in ventas),
        ),
        '## Productos a reponer (stock ≤ 5)\n\n' + tabla(
            ('Producto', 'Stock'),
            ((fila['nombre'], fila['stock']) for fila in stock),
        ),
        '## Clientes frecuentes (al menos 2 pedidos pagados)\n\n' + tabla(
            ('Cliente', 'Pedidos pagados'),
            ((fila['nombre'], fila['pedidos_pagados']) for fila in clientes),
        ),
    ]) + '\n'


def main():
    try:
        contenido = generar_reporte()
        REPORTE.write_text(contenido, encoding='utf-8')
    except (OSError, RuntimeError, KeyError, TypeError) as error:
        print(f'No se pudo generar el reporte: {error}', file=sys.stderr)
        return 1
    print(f'Reporte generado: {REPORTE}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
