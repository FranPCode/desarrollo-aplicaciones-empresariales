"""PARTE 1 — Las seis consultas del ORM. Son la única «puerta» a los datos: las usan la CLI (Parte 2)
y el servidor MCP (Parte 3), así que lo que devuelvan aquí es lo que verá una persona, un script o un agente.

Reglas:
- Todo con el ORM: filter, exclude, Q, F, annotate, aggregate, select_related… Nada de recorrer tablas
  enteras en Python para filtrar o sumar, y nada de SQL a mano.
- Devuelvan datos simples (listas, diccionarios, números, Decimal): no QuerySets ni objetos del modelo.
- Los importes son Decimal: no los conviertan a float.

Comprueben su avance con: python manage.py duelo
Los datos son fijos (`python manage.py cargar_datos`), así que cada pregunta tiene una respuesta conocida.
"""

from decimal import Decimal

from django.db.models import Count, F, Q, Sum

from tienda.models import Cliente, LineaPedido, Pedido, Producto


def productos_por_categoria(nombre):
    """Productos de la categoría `nombre`, ordenados por nombre.

    El nombre de la categoría NO distingue mayúsculas: «gaseosas» y «Gaseosas» dan lo mismo.
    Devuelve [{'nombre', 'precio', 'stock', 'descripcion'}, ...]; lista vacía si la categoría no existe.
    """
    return list(
        Producto.objects.filter(categoria__nombre__iexact=nombre)
        .order_by('nombre')
        .values('nombre', 'precio', 'stock', 'descripcion')
    )


def buscar_productos(texto):
    """Nombres de los productos cuyo nombre O descripción contienen `texto` (sin distinguir mayúsculas),
    ordenados. Pista: una condición O entre dos campos se escribe con objetos Q.
    """
    return list(
        Producto.objects.filter(Q(nombre__icontains=texto) | Q(descripcion__icontains=texto))
        .order_by('nombre')
        .values_list('nombre', flat=True)
    )


def stock_bajo(umbral=5):
    """Productos con stock menor o igual a `umbral`, del que menos tiene al que más (y por nombre si empatan).
    Devuelve [{'nombre', 'stock'}, ...].
    """
    return list(
        Producto.objects.filter(stock__lte=umbral)
        .order_by('stock', 'nombre')
        .values('nombre', 'stock')
    )


def ventas_por_categoria():
    """Importe vendido por categoría, contando SOLO los pedidos pagados, de mayor a menor.

    El importe de una línea es cantidad × precio_unitario (el precio al momento de la venta, no el actual).
    Devuelve [{'categoria', 'total'}, ...] con `total` en Decimal.
    Pista: values() para agrupar, annotate(Sum(...)) para sumar y F() para multiplicar dos campos.
    """
    return list(
        LineaPedido.objects.filter(pedido__estado=Pedido.PAGADO)
        .values(categoria=F('producto__categoria__nombre'))
        .annotate(total=Sum(F('cantidad') * F('precio_unitario')))
        .order_by('-total', 'categoria')
    )


def clientes_frecuentes(minimo=2):
    """Clientes con al menos `minimo` pedidos PAGADOS (los pendientes y anulados no cuentan), de más a menos
    pedidos y por nombre si empatan. Devuelve [{'nombre', 'pedidos_pagados'}, ...].
    Pista: Count admite un filter=Q(...).
    """
    return list(
        Cliente.objects.annotate(
            pedidos_pagados=Count('pedidos', filter=Q(pedidos__estado=Pedido.PAGADO))
        )
        .filter(pedidos_pagados__gte=minimo)
        .order_by('-pedidos_pagados', 'nombre')
        .values('nombre', 'pedidos_pagados')
    )


def detalle_pedido(pedido_id):
    """Detalle de un pedido, o None si no existe.

    Devuelve {'pedido', 'cliente' (nombre), 'estado', 'lineas': [{'producto', 'cantidad', 'precio_unitario',
    'subtotal'}], 'total'} con importes en Decimal.
    Tiene que resolverse en DOS consultas a la base de datos, tenga las líneas que tenga: una para el pedido
    con su cliente y otra para las líneas con su producto (select_related).
    """
    try:
        pedido = Pedido.objects.select_related('cliente').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        return None

    lineas = []
    total = Decimal('0')
    for linea in LineaPedido.objects.filter(pedido=pedido).select_related('producto').order_by('id'):
        subtotal = linea.cantidad * linea.precio_unitario
        lineas.append({
            'producto': linea.producto.nombre,
            'cantidad': linea.cantidad,
            'precio_unitario': linea.precio_unitario,
            'subtotal': subtotal,
        })
        total += subtotal

    return {
        'pedido': pedido.pk,
        'cliente': pedido.cliente.nombre,
        'estado': pedido.estado,
        'lineas': lineas,
        'total': total,
    }
