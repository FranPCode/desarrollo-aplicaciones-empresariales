"""Versión escrita por un asistente de IA a partir del enunciado del laboratorio.

No editen este archivo: es el punto de partida del duelo (Parte 4). Para corregirlo,
cópienlo con `python manage.py duelo --iniciar-corregida` y editen tienda/corregida/.
"""

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum

from tienda.models import Cliente, LineaPedido, Pedido, Producto


def productos_por_categoria(nombre):
    productos = Producto.objects.filter(categoria__nombre=nombre).order_by('nombre')
    return [{'nombre': p.nombre, 'precio': p.precio, 'stock': p.stock, 'descripcion': p.descripcion}
            for p in productos]


def buscar_productos(texto):
    productos = Producto.objects.filter(nombre__icontains=texto, descripcion__icontains=texto)
    return [p.nombre for p in productos.order_by('nombre')]


def stock_bajo(umbral=5):
    productos = Producto.objects.filter(stock__lte=umbral).order_by('stock', 'nombre')
    return [{'nombre': p.nombre, 'stock': p.stock} for p in productos]


def ventas_por_categoria():
    importe = ExpressionWrapper(F('cantidad') * F('precio_unitario'),
                                output_field=DecimalField(max_digits=10, decimal_places=2))
    filas = (LineaPedido.objects
             .values('producto__categoria__nombre')
             .annotate(total=Sum(importe))
             .order_by('-total'))
    return [{'categoria': f['producto__categoria__nombre'], 'total': f['total']} for f in filas]


def clientes_frecuentes(minimo=2):
    clientes = (Cliente.objects
                .annotate(pedidos_pagados=Count('pedidos', filter=Q(pedidos__estado=Pedido.PAGADO)))
                .filter(pedidos_pagados__gte=minimo)
                .order_by('-pedidos_pagados', 'nombre'))
    return [{'nombre': c.nombre, 'pedidos_pagados': c.pedidos_pagados} for c in clientes]


def detalle_pedido(pedido_id):
    pedido = Pedido.objects.filter(pk=pedido_id).first()
    if pedido is None:
        return None
    lineas = [{'producto': linea.producto.nombre, 'cantidad': linea.cantidad,
               'precio_unitario': linea.precio_unitario,
               'subtotal': linea.cantidad * linea.precio_unitario}
              for linea in pedido.lineas.all()]
    return {'pedido': pedido.pk, 'cliente': pedido.cliente.nombre, 'estado': pedido.estado,
            'lineas': lineas, 'total': sum((linea['subtotal'] for linea in lineas), 0)}
