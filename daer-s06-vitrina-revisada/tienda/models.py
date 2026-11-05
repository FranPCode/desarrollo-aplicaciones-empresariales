from django.db import models

# Categoria y Producto son los del Lab 6 regular. La descripción la escribe el asistente de IA
# de la tienda (tienda/datos/descripciones_ia.json): es texto de un tercero, no código.
# Este archivo ya está completo: no hace falta tocarlo.


class Categoria(models.Model):
    nombre = models.CharField(max_length=200)
    pub_date = models.DateTimeField('fecha de registro', auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')
    descripcion = models.TextField('descripción (la escribe el asistente de IA)', blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
