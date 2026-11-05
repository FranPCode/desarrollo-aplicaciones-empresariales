# Lab extra S06 — La vitrina revisada por pruebas

La tienda del Lab 6 (categorías y productos) tiene una **vitrina** pública: la portada, una página por
categoría y una por producto. Las **descripciones de los productos las escribió un asistente de IA**
(`tienda/datos/descripciones_ia.json`), y dos traen sorpresas.

Ustedes, **en pareja**, escriben las plantillas de la vitrina contra pruebas automáticas:

1. la **plantilla base** con herencia, estáticos y menú lateral (Parte 1);
2. la **portada**, la **categoría** y la **tarjeta** que comparten (Parte 2);
3. el **detalle**, que muestra el texto de la IA como texto (Parte 3).

Luego corren las mismas pruebas contra unas plantillas que **escribió un asistente de IA**, encuentran
sus cuatro fallos y los corrigen (Parte 4). La guía de laboratorio tiene el paso a paso.

## Empezar

Un integrante copia este repositorio con **Use this template** y agrega al otro como colaborador.

```powershell
python -m venv myvenv
myvenv\Scripts\activate
pip install django
python manage.py migrate
python manage.py cargar_datos          # 5 categorías (una vacía), 10 productos y las descripciones de la IA
python manage.py createsuperuser
python manage.py duelo                 # casi todo en rojo: es lo esperado
```

## Comandos

| Comando | Para qué |
|---|---|
| `python manage.py duelo` | Corre las pruebas contra **sus** plantillas (`tienda/alumno/templates/`) y resume por parte |
| `python manage.py duelo --detalle` | Además, el error de cada prueba en rojo |
| `python manage.py runserver` | La vitrina en `http://localhost:8000/tienda/` con sus plantillas |
| `python manage.py duelo ia` | Las mismas pruebas contra las plantillas de la IA (Parte 4) |
| `python manage.py duelo --iniciar-corregida` | Copia `tienda/ia/` a `tienda/corregida/` para corregirla |
| `python manage.py duelo corregida` | Las pruebas contra su copia corregida |

Para ver en el navegador otra versión, en PowerShell: `$env:TIENDA_VERSION = "ia"; python manage.py runserver`
(y `Remove-Item Env:TIENDA_VERSION` para volver a la suya).

## Estructura

| Carpeta o archivo | Qué es | ¿Lo editan? |
|---|---|---|
| `tienda/alumno/templates/` | **Sus plantillas**: `layout.html` (Parte 1), `_tarjeta.html`, `index.html`, `categoria.html` (Parte 2), `producto.html` (Parte 3). Cada una explica en su cabecera qué tiene que hacer | Sí |
| `tienda/ia/templates/` | Las plantillas que escribió un asistente de IA | **No** |
| `tienda/corregida/templates/` | Su copia de las de la IA, corregida (la crea `duelo --iniciar-corregida`) | Sí (Parte 4) |
| `tienda/tests/` | Las pruebas: el oráculo del laboratorio | **No** |
| `tienda/views.py` | Las vistas, ya hechas: dicen qué variables recibe cada plantilla | No |
| `tienda/static/` | Bootstrap 4, jQuery y `css/shop.css` | No |
| `referencia/` | La plantilla HTML de la tienda (Start Bootstrap «Shop Homepage», MIT), de donde sale `layout.html` | No |

Las descripciones del asistente y las plantillas de `tienda/ia/` están **escritas a mano** imitando
fallos típicos de un modelo; no salen de un modelo concreto.

## Entregar

El repositorio de la pareja (sin `myvenv/` ni `db.sqlite3`: el `.gitignore` ya los excluye), con commits de
los dos integrantes, y el informe con las tablas y capturas, **una sola vez por pareja**, como segunda
entrega de laboratorio de la semana 6.
