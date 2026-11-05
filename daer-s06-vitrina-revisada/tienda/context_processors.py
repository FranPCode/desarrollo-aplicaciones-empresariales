from .models import Categoria


def categorias(request):
    """Las categorías del menú lateral, disponibles en todas las plantillas como `categorias`."""
    return {'categorias': Categoria.objects.all()}
