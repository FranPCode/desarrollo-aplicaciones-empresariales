"""Parte 1 — La plantilla base: herencia, estáticos y menú lateral."""

from django.contrib.staticfiles import finders
from django.test.utils import override_settings
from django.urls import reverse

from .base import VitrinaTestCase


class BaseTests(VitrinaTestCase):
    def test_todas_las_paginas_heredan_del_layout(self):
        paginas = [self.get('index'), self.detalle('Fanta 500ml'), self.get('categoria', self.categoria('Snacks').id)]
        for r in paginas:
            self.assertEqual(r.status_code, 200)
            self.assertTemplateUsed(r, 'layout.html')

    def test_carga_bootstrap_y_la_hoja_propia(self):
        r = self.get('index')
        for ruta in ('vendor/bootstrap/css/bootstrap.min.css', 'css/shop.css',
                     'vendor/jquery/jquery.min.js', 'vendor/bootstrap/js/bootstrap.bundle.min.js'):
            self.assertIsNotNone(finders.find(ruta))
            self.assertContains(r, f'/static/{ruta}')

    @override_settings(STATIC_URL='/estaticos/')
    def test_estaticos_con_static_y_no_a_mano(self):
        # Si el sitio publica sus estáticos en otra dirección, solo {% static %} se entera.
        r = self.get('index')
        self.assertContains(r, '/estaticos/css/shop.css')
        self.assertNotContains(r, '"/static/')

    def test_titulo_de_cada_pagina(self):
        self.assertContains(self.detalle('Cheetos'), '<title>Cheetos')
        self.assertContains(self.get('categoria', self.categoria('Galletas').id), '<title>Galletas')

    def test_menu_lateral_con_las_categorias(self):
        for r in (self.get('index'), self.detalle('Fanta 500ml')):
            for nombre in ('Chocolates', 'Galletas', 'Gaseosas', 'Helados', 'Snacks'):
                cat = self.categoria(nombre)
                self.assertContains(r, f'href="{reverse("categoria", args=[cat.id])}"')
                self.assertContains(r, nombre)
        self.assertContains(self.get('index'), f'href="{reverse("index")}"')

    def test_categoria_activa_en_el_menu(self):
        r = self.get('categoria', self.categoria('Snacks').id)
        self.assertContains(r, 'active', count=1)
        self.assertNotContains(self.get('index'), 'list-group-item active')
