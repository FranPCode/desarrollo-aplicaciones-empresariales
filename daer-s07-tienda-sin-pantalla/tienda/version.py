"""Elige de qué carpeta salen las consultas del ORM que usan la CLI y el servidor MCP.

Hay cuatro versiones de consultas.py:

    alumno     tienda/alumno/      la suya: la que completan en la Parte 1
    ia         tienda/ia/          la que «escribió un asistente de IA»: no se toca
    corregida  tienda/corregida/   su copia de la de la IA, con sus fallos arreglados (Parte 4)
    solucion   teacher/solucion/   la del docente; no viene en su copia del repositorio

La versión activa sale de settings.TIENDA_VERSION. No hace falta tocar este archivo.
"""

import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSIONES = {
    'alumno': 'tienda.alumno',
    'ia': 'tienda.ia',
    'corregida': 'tienda.corregida',
    'solucion': 'teacher.solucion',
}


def paquete():
    version = settings.TIENDA_VERSION
    if version not in VERSIONES:
        raise ImproperlyConfigured(f'TIENDA_VERSION={version!r}: tiene que ser una de {", ".join(VERSIONES)}')
    return VERSIONES[version]


def modulo(nombre):
    """El módulo `nombre` (consultas) de la versión activa."""
    ruta = f'{paquete()}.{nombre}'
    try:
        return importlib.import_module(ruta)
    except ModuleNotFoundError as e:
        if e.name is None or not ruta.startswith(e.name):
            raise  # falta otra cosa que el módulo importa: que se vea el error real
        if settings.TIENDA_VERSION == 'corregida':
            raise ImproperlyConfigured(
                'Todavía no existe tienda/corregida/. Créala con: python manage.py duelo --iniciar-corregida'
            ) from None
        if settings.TIENDA_VERSION == 'solucion':
            raise ImproperlyConfigured('La versión «solucion» no está disponible en esta copia.') from None
        raise
