"""De qué carpeta salen las plantillas de la vitrina.

    alumno     tienda/alumno/templates/      las suyas: las que completan en las partes 1 a 3
    ia         tienda/ia/templates/          las que «escribió un asistente de IA»: no se tocan
    corregida  tienda/corregida/templates/   su copia de las de la IA, corregida (Parte 4)
    solucion   teacher/solucion/templates/   las del docente; no vienen en su copia del repositorio

La versión activa sale de la variable de entorno TIENDA_VERSION (por defecto, alumno).
No hace falta tocar este archivo.
"""

import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

VERSIONES = {
    'alumno': BASE / 'tienda' / 'alumno' / 'templates',
    'ia': BASE / 'tienda' / 'ia' / 'templates',
    'corregida': BASE / 'tienda' / 'corregida' / 'templates',
    'solucion': BASE / 'teacher' / 'solucion' / 'templates',
}


def carpeta_de_plantillas():
    version = os.environ.get('TIENDA_VERSION', 'alumno')
    if version not in VERSIONES:
        raise SystemExit(f'TIENDA_VERSION={version!r}: tiene que ser una de {", ".join(VERSIONES)}')
    carpeta = VERSIONES[version]
    if not carpeta.is_dir():
        if version == 'corregida':
            raise SystemExit('Todavía no existe tienda/corregida/. Créala con: python manage.py duelo --iniciar-corregida')
        raise SystemExit(f'La versión «{version}» no está disponible en esta copia.')
    return version, carpeta
