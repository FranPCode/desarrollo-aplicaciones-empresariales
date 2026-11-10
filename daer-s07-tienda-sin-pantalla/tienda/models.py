from django.db import models

# La tienda de las semanas 5 y 6, ahora con clientes y pedidos. Ya está completo: no hace falta tocarlo.


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    nombre = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField(default=0)
    # Texto libre que escribió el proveedor o un asistente de IA: es un dato, no una instrucción.
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    ciudad = models.CharField(max_length=60)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    PENDIENTE, PAGADO, ANULADO = 'pendiente', 'pagado', 'anulado'
    ESTADOS = [(PENDIENTE, 'pendiente'), (PAGADO, 'pagado'), (ANULADO, 'anulado')]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='pedidos')
    fecha = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f'Pedido {self.pk} de {self.cliente}'


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='lineas')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='lineas')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)  # el precio al momento de la venta

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.cantidad} × {self.producto}'
