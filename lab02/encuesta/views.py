from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'titulo': "Formulario",
    }
    return render(request, 'encuesta/formulario.html', context)

def enviar(request):
    context = {
        'titulo': "Respuesta",
        'nombre' : request.POST['nombre'],
        'clave': request.POST['password'],
        'educacion': request.POST['educacion'],
        'nacionalidad': request.POST['nacionalidad'],
        'idiomas': request.POST.getlist('idiomas'),
        'correo': request.POST['email'],
        'website': request.POST['sitioweb'],
    }
    return render(request, 'encuesta/respuesta.html', context)
    

def operacion(request):
    return render(request, 'encuesta/operacion.html')

def resultado_operacion(request):
    numero1 = float(request.POST['numero1'])
    numero2 = float(request.POST['numero2'])
    operacion = request.POST['operacion']

    if operacion == 'suma':
        resultado = numero1 + numero2
        nombre_operacion = 'suma'
        simbolo = '+'
    elif operacion == 'resta':
        resultado = numero1 - numero2
        nombre_operacion = 'resta'
        simbolo = '-'
    else:
        resultado = numero1 * numero2
        nombre_operacion = 'multiplicación'
        simbolo = '*'

    context = {
        'numero1': numero1,
        'numero2': numero2,
        'nombre_operacion': nombre_operacion,
        'simbolo': simbolo,
        'resultado': resultado,
    }
    return render(request, 'encuesta/resultado_operacion.html', context)

def cilindro(request):
    return render(request, 'encuesta/cilindro.html')

def resultado_cilindro(request):
    altura = float(request.POST['altura'])
    diametro = float(request.POST['diametro'])
    volumen = 3.1416 * (diametro / 2) ** 2 * altura

    context = {
        'altura': altura,
        'diametro': diametro,
        'volumen': volumen,
    }
    return render(request, 'encuesta/resultado_cilindro.html', context)


