"""Lo comparten la CLI y el servidor MCP: pasar lo que devuelven las consultas a JSON.

Los importes son Decimal (dinero exacto). En JSON viajan como texto, «1.80», para no perder céntimos.
"""

import json
from decimal import Decimal


def a_json(valor):
    if isinstance(valor, Decimal):
        return f'{valor:.2f}'
    if isinstance(valor, dict):
        return {k: a_json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [a_json(v) for v in valor]
    return valor


def volcar(valor):
    return json.dumps(a_json(valor), ensure_ascii=False, indent=2)
