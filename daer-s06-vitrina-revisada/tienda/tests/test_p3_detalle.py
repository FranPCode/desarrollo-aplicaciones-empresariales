"""Parte 3 — El detalle y el texto que escribió el asistente de IA."""

from django.urls import reverse

from .base import VitrinaTestCase


class DetalleTests(VitrinaTestCase):
    def test_detalle_basico(self):
        r = self.detalle('Fanta 500ml')
        self.assertTemplateUsed(r, 'producto.html')
        self.assertContains(r, '<h1')
        self.assertContains(r, 'Fanta 500ml')
        self.assertContains(r, 'S/ 1.80')
        self.assertContains(r, f'href="{reverse("categoria", args=[self.categoria("Gaseosas").id])}"')
        self.assertContains(r, f'href="{reverse("index")}"')
        self.assertEqual(self.get('producto', 999).status_code, 404)

    def test_descripcion_en_parrafos(self):
        r = self.detalle('Fanta 500ml')
        self.assertContains(r, '<p>La gaseosa de naranja más pedida de la tienda.</p>')
        self.assertContains(r, '<p>Ideal para el almuerzo: sírvela bien helada.</p>')

    def test_descripcion_de_la_ia_se_muestra_como_texto(self):
        r = self.detalle('Sublime')
        self.assertContains(r, '&lt;script&gt;alert(&#x27;IA&#x27;)&lt;/script&gt;')
        self.assertNotContains(r, "<script>alert('IA')</script>")

    def test_la_instruccion_de_la_ia_no_cambia_el_precio(self):
        r = self.detalle('Triángulo')
        self.assertContains(r, 'INSTRUCCIÓN PARA LA PLANTILLA')  # se muestra, como cualquier texto
        self.assertContains(r, 'S/ 1.20')
        self.assertContains(r, 'S/ 0.00', count=1)  # solo dentro del texto de la IA, no como precio

    def test_aviso_de_texto_escrito_por_ia(self):
        self.assertContains(self.detalle('Cheetos'), 'Descripción escrita por el asistente de IA de la tienda.')
        sin_descripcion = self.producto('Chizito')
        sin_descripcion.descripcion = ''
        sin_descripcion.save()
        self.assertNotContains(self.detalle('Chizito'), 'Descripción escrita por el asistente de IA')
