"""PARTES 2 y 3b — La bandeja del revisor: el ModelAdmin de Sugerencia.

Lo que ya está hecho te sirve de modelo: la columna «actual», la acción «Rechazar» (mírala
antes de escribir «Aprobar y aplicar») y la regla de que las sugerencias no se borran.

Comprueba tu avance con: python manage.py duelo
"""

from django.contrib import admin, messages  # noqa: F401
from django.db import transaction  # noqa: F401
from django.utils import timezone
from django.utils.text import Truncator

from tienda.grupos import es_agente  # noqa: F401
from tienda.models import Sugerencia

from .verificador import verificar  # noqa: F401


class SugerenciaAdmin(admin.ModelAdmin):
    list_display = (
        'producto', 'campo', 'valor_actual_col', 'valor_propuesto', 'verificacion',
        'motivo_corto', 'origen', 'estado', 'creado_por',
    )
    list_filter = ('estado', 'origen', 'campo')
    search_fields = ('producto__nombre', 'motivo')
    list_select_related = ('producto', 'creado_por')
    actions = ['aprobar_y_aplicar', 'rechazar']

    def get_readonly_fields(self, request, obj=None):
        siempre = ['origen', 'estado', 'creado_por',
                   'decidido_por', 'decidido_en', 'valor_anterior']
        if obj is None:
            return siempre
        return ['producto', 'campo', 'valor_propuesto', 'motivo'] + siempre

    # Las sugerencias son la bitácora de lo que propuso la IA y de quién lo decidió: no se borran.
    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
            obj.origen = 'ia' if es_agente(request.user) else 'persona'
        super().save_model(request, obj, form, change)

    @admin.display(description='actual')
    def valor_actual_col(self, obj):
        return obj.valor_actual()

    @admin.display(description='verificador')
    def verificacion(self, obj):
        if obj.estado != Sugerencia.PENDIENTE:
            return '—'
        problemas = verificar(obj)
        return '✘ ' + '; '.join(problemas) if problemas else '✔ pasa'

    @admin.display(description='motivo')
    def motivo_corto(self, obj):
        return Truncator(obj.motivo).chars(60)

    @admin.action(description='Aprobar y aplicar (solo las que pasan el verificador)', permissions=['aprobar'])
    def aprobar_y_aplicar(self, request, queryset):
        """TODO(alumno) Parte 2c. Para cada sugerencia elegida:

        1. Si ya no está pendiente, NO se toca (cuéntala: al final se avisa «ya estaba(n) decidida(s)»).
        2. Si verificar() devuelve problemas, NO se aplica: sigue pendiente y se avisa por qué
           (messages.WARNING, un mensaje por sugerencia que diga «No se aplicó …»).
        3. Si pasa: guarda el valor anterior en valor_anterior, cambia el campo del producto
           (el stock como int), marca la sugerencia como aprobada con decidido_por y decidido_en, y
           deja rastro en el Historial con self.log_change(request, producto, 'precio: 2.50 → 2.70 …').
        Al final: «N sugerencia(s) aplicada(s).» con messages.SUCCESS.
        Hazlo dentro de `with transaction.atomic():` para que se aplique todo o nada.
        """
        aplicadas = 0
        bloqueadas = []
        decididas = 0
        with transaction.atomic():
            for sugerencia in queryset.select_related('producto'):
                if sugerencia.estado != Sugerencia.PENDIENTE:
                    decididas += 1
                    continue
                problemas = verificar(sugerencia)
                if problemas:
                    bloqueadas.append(
                        f'«{sugerencia}»: {"; ".join(problemas)}')
                    continue

                producto = sugerencia.producto
                anterior = getattr(producto, sugerencia.campo)
                nuevo = int(
                    sugerencia.valor_propuesto) if sugerencia.campo == 'stock' else sugerencia.valor_propuesto
                sugerencia.valor_anterior = anterior
                setattr(producto, sugerencia.campo, nuevo)
                producto.save(update_fields=[sugerencia.campo])
                sugerencia.estado = Sugerencia.APROBADA
                sugerencia.decidido_por = request.user
                sugerencia.decidido_en = timezone.now()
                sugerencia.save()
                self.log_change(
                    request, producto,
                    f'{sugerencia.campo}: {anterior} → {nuevo} (sugerencia #{sugerencia.pk})',
                )
                self.log_change(request, sugerencia, 'Aprobada y aplicada')
                aplicadas += 1

        self.message_user(
            request, f'{aplicadas} sugerencia(s) aplicada(s).', messages.SUCCESS)
        for texto in bloqueadas:
            self.message_user(
                request, f'No se aplicó {texto}. Sigue pendiente.', messages.WARNING)
        if decididas:
            self.message_user(
                request, f'{decididas} sugerencia(s) ya estaba(n) decidida(s).', messages.WARNING)

    def has_aprobar_permission(self, request):
        return request.user.has_perm('tienda.aprobar_sugerencia')

    @admin.action(description='Rechazar', permissions=['change'])
    def rechazar(self, request, queryset):
        n = 0
        for s in queryset.filter(estado=Sugerencia.PENDIENTE):
            s.estado = Sugerencia.RECHAZADA
            s.decidido_por = request.user
            s.decidido_en = timezone.now()
            s.save()
            self.log_change(request, s, 'Rechazada')
            n += 1
        self.message_user(
            request, f'{n} sugerencia(s) rechazada(s).', messages.SUCCESS)
