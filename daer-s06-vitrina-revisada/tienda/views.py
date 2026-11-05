"""Las vistas de la vitrina. Ya están hechas: lo que se escribe en este laboratorio son las plantillas.

Cada vista dice qué variables recibe su plantilla. Además, TODAS las plantillas reciben
`categorias` (las del menú lateral) desde tienda/context_processors.py.
"""

from django.shortcuts import get_object_or_404, render

from .models import Categoria, Producto


def index(request):
    # index.html recibe: product_list (los 6 primeros por nombre)
    product_list = Producto.objects.select_related('categoria')[:6]
    return render(request, 'index.html', {'product_list': product_list})


def producto(request, producto_id):
    # producto.html recibe: producto
    producto = get_object_or_404(Producto.objects.select_related('categoria'), pk=producto_id)
    return render(request, 'producto.html', {'producto': producto})


def categoria(request, categoria_id):
    # categoria.html recibe: categoria y product_list (sus productos)
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    product_list = categoria.producto_set.select_related('categoria')
    return render(request, 'categoria.html', {'categoria': categoria, 'product_list': product_list})
