import subprocess
import unittest
from unittest.mock import patch

import reporte


class ReporteTests(unittest.TestCase):
    @patch('reporte.subprocess.run')
    def test_consulta_usa_json_y_conserva_importes_como_texto(self, ejecutar):
        ejecutar.return_value = subprocess.CompletedProcess([], 0, '[{"total": "8.40"}]', '')
        self.assertEqual(reporte.consultar('ventas'), [{'total': '8.40'}])
        self.assertEqual(ejecutar.call_args.args[0][-2:], ['ventas', '--json'])

    @patch('reporte.subprocess.run')
    def test_consulta_informa_codigo_de_error(self, ejecutar):
        ejecutar.return_value = subprocess.CompletedProcess([], 2, '', 'argumento inválido')
        with self.assertRaisesRegex(RuntimeError, 'código 2: argumento inválido'):
            reporte.consultar('stock', '--umbral', '-1')

    @patch('reporte.subprocess.run')
    def test_consulta_rechaza_json_invalido(self, ejecutar):
        ejecutar.return_value = subprocess.CompletedProcess([], 0, 'no es JSON', '')
        with self.assertRaisesRegex(RuntimeError, 'JSON válido'):
            reporte.consultar('ventas')

    @patch('reporte.consultar')
    def test_reporte_incluye_las_tres_secciones(self, consultar):
        consultar.side_effect = [
            [{'categoria': 'A|B', 'total': '8.40'}],
            [{'nombre': 'Producto', 'stock': 1}],
            [{'nombre': 'Cliente', 'pedidos_pagados': 2}],
        ]
        contenido = reporte.generar_reporte()
        self.assertIn('| A\\|B | 8.40 |', contenido)
        self.assertIn('| Producto | 1 |', contenido)
        self.assertIn('| Cliente | 2 |', contenido)
        self.assertEqual(consultar.call_count, 3)

    @patch('reporte.REPORTE')
    @patch('reporte.consultar')
    def test_error_no_escribe_reporte(self, consultar, destino):
        consultar.side_effect = RuntimeError('falló la consulta')
        with patch('sys.stderr'):
            self.assertEqual(reporte.main(), 1)
        destino.write_text.assert_not_called()


if __name__ == '__main__':
    unittest.main()
