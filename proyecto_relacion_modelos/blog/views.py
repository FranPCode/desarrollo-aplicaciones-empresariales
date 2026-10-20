from django.shortcuts import get_object_or_404, render
from .models import Autor, Entrada


def lista_entradas(request):
    entradas = Entrada.objects.select_related('autor').all()
    return render(request, 'blog/lista_entradas.html', {'entradas': entradas})


def entradas_por_autor(request, autor_id):
    autor = get_object_or_404(Autor, id=autor_id)
    entradas = Entrada.objects.filter(autor=autor).select_related('autor')
    return render(
        request,
        'blog/lista_entradas.html',
        {'entradas': entradas, 'autor_seleccionado': autor},
    )
