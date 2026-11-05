"""Carga la tienda del Lab 6 (4 categorías, 10 productos) más las descripciones que escribió el
asistente de IA (tienda/datos/descripciones_ia.json) y una categoría vacía («Helados»).

Las descripciones están escritas a mano imitando lo que puede devolver un modelo, no salen de uno
real: dos traen sorpresas (HTML y una «instrucción»). Se puede repetir: no duplica.
"""

import json
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from tienda.models import Categoria, Producto

DATOS = [
    ('Gaseosas', 'Fanta 500ml', '1.80', 10), ('Gaseosas', 'Coca Cola 500ml', '2.50', 10),
    ('Gaseosas', '7up 500ml', '1.70', 0), ('Snacks', 'Cheetos', '1.00', 12),
    ('Snacks', 'Chizito', '1.00', 12), ('Galletas', 'Picaras', '1.00', 12),
    ('Galletas', 'Coronita Fresa', '0.70', 12), ('Chocolates', 'Princesa', '1.50', 8),
    ('Chocolates', 'Sublime', '1.50', 8), ('Chocolates', 'Triángulo', '1.20', 3),
]
DESCRIPCIONES = Path(__file__).resolve().parents[2] / 'datos' / 'descripciones_ia.json'


class Command(BaseCommand):
    help = 'Carga categorías, productos y las descripciones del asistente de IA.'

    def handle(self, *args, **options):
        descripciones = json.loads(DESCRIPCIONES.read_text(encoding='utf-8'))
        for cat, nombre, precio, stock in DATOS:
            categoria, _ = Categoria.objects.get_or_create(nombre=cat)
            Producto.objects.update_or_create(nombre=nombre, defaults={
                'categoria': categoria, 'precio': Decimal(precio), 'stock': stock,
                'pub_date': timezone.now(), 'descripcion': descripciones.get(nombre, ''),
            })
        Categoria.objects.get_or_create(nombre='Helados')
        self.stdout.write(self.style.SUCCESS(
            f'{Categoria.objects.count()} categorías y {Producto.objects.count()} productos. '
            'Abre http://localhost:8000/tienda/'))
