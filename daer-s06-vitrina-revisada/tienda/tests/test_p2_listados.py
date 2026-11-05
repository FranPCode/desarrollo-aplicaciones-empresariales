"""Parte 2 — Portada, categoría y la tarjeta compartida: bucles, filtros, condicionales e include."""

import re

from django.urls import reverse

from .base import VitrinaTestCase


class ListadosTests(VitrinaTestCase):
    def test_portada_con_seis_tarjetas(self):
        r = self.get('index')
        self.assertTemplateUsed(r, 'index.html')
        self.assertTemplateUsed(r, '_tarjeta.html')
        for nombre in ('7up 500ml', 'Cheetos', 'Chizito', 'Coca Cola 500ml', 'Coronita Fresa', 'Fanta 500ml'):
            self.assertContains(r, nombre)
        self.assertNotContains(r, 'Triángulo')

    def test_precio_con_punto_y_dos_decimales(self):
        r = self.get('index')
        self.assertContains(r, 'S/ 1.80')
        self.assertContains(r, 'S/ 0.70')
        self.assertNotContains(r, 'S/ 1,80')

    def test_descripcion_recortada_en_la_tarjeta(self):
        r = self.get('categoria', self.categoria('Galletas').id)
        self.assertContains(r, 'Galletas con relleno de chocolate y una cobertura crocante')
        self.assertContains(r, '…')
        self.assertNotContains(r, 'se deshace en la boca', msg_prefix='la tarjeta no recorta la descripción a 80 caracteres')
        self.assertNotContains(r, 'Paquete individual')

    def test_stock_con_condicionales(self):
        r = self.get('index')
        self.assertContains(r, 'Agotado')  # 7up, stock 0
        self.assertContains(r, 'Stock: 12')
        r = self.get('categoria', self.categoria('Chocolates').id)
        self.assertContains(r, '¡Últimas 3 unidades!')  # Triángulo
        self.assertContains(r, 'Stock: 8')

    def test_categoria_lista_solo_sus_productos(self):
        r = self.get('categoria', self.categoria('Gaseosas').id)
        self.assertTemplateUsed(r, 'categoria.html')
        self.assertTemplateUsed(r, '_tarjeta.html')
        self.assertContains(r, '<h2')
        for nombre in ('Fanta 500ml', 'Coca Cola 500ml', '7up 500ml'):
            self.assertContains(r, nombre)
        self.assertNotContains(r, 'Cheetos')
        self.assertContains(r, '3 productos')

    def test_categoria_vacia(self):
        r = self.get('categoria', self.categoria('Helados').id)
        self.assertContains(r, 'No hay productos en esta categoría.')

    def test_enlaces_de_las_tarjetas(self):
        # Un enlace relativo «producto/1/» funciona en la portada y se rompe en /tienda/categoria/1/.
        for r in (self.get('index'), self.get('categoria', self.categoria('Gaseosas').id)):
            fanta = self.producto('Fanta 500ml')
            self.assertContains(r, f'href="{reverse("producto", args=[fanta.id])}"')
            self.assertFalse(re.search(r'href="producto/', r.content.decode()), 'hay enlaces relativos a producto/')
