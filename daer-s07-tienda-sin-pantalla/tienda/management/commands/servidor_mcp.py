"""Arranca el servidor MCP de la tienda por stdio: `python manage.py servidor_mcp`.

No lo ejecuten «a mano» para usarlo: lo lanza el cliente MCP (Claude Code, VS Code, opencode, el Inspector).
Por stdio la salida estándar es del protocolo: nada de print() en este proceso.
"""

from django.core.management.base import BaseCommand

from tienda.servidor_mcp import crear_servidor


class Command(BaseCommand):
    help = 'Servidor MCP de la tienda (stdio, solo lectura).'
    requires_system_checks = []

    def handle(self, *args, **options):
        crear_servidor().run(transport='stdio')
