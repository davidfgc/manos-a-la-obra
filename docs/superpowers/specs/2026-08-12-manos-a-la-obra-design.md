# Manos a la Obra — Diseño (MVP)

- **Fecha:** 2026-08-12
- **Estado:** Aprobado el diseño; pendiente revisión del spec antes del plan de implementación.

## Contexto y propósito

Sitio web para **centralizar información de ayuda para el terremoto en Colombia**.
Reúne recursos dispersos en un solo lugar de consulta rápida, usable desde un celular
con conexión pobre.

El MVP se enfoca en **mostrar información curada de solo lectura**. La colaboración de
terceros (envíos + moderación con base de datos) es una **Fase 2** explícitamente diferida.

## Alcance

**Dentro del MVP (Fase 1):**
- Dos categorías de contenido: **archivos 3D para imprimir** y **puntos de acopio**.
- Contenido curado por el mantenedor, editando un archivo versionado en git.
- Puntos de acopio filtrables por **país** y **ciudad**, con link a Google Maps.
- Canal para aportar información: **link a la cuenta de X** del mantenedor
  (`https://x.com/davidfgonzalezc`). La gente escribe por ahí; el mantenedor agrega el
  contenido a mano y hace push.
- Deploy en Railway.

**Fuera del MVP (Fase 2, documentada más abajo):**
- Base de datos (Postgres en Railway).
- Formulario de envío anónimo de terceros.
- Login de admin y cola de moderación.
- Categorías adicionales (necesidades/pedidos de ayuda, recursos/guías).
- Mapa interactivo.
- Internacionalización (el MVP es solo en español).

## Arquitectura

**Stack:** Python 3.13 · Flask (app factory + blueprints) · Jinja2 · Pico CSS (CDN) ·
gunicorn (producción) · pytest. Gestión de paquetes con **uv**. Deploy con **Nixpacks** a Railway.

Sin base de datos, sin sesión, sin autenticación en el MVP. El contenido vive en un
archivo YAML versionado.

**Pieza central — la capa repositorio (`services/contenido.py`):** es la única que sabe
de dónde salen los datos. Expone una interfaz estable que rutas y plantillas consumen.
En Fase 2 se reemplaza su implementación (YAML → Postgres) **sin tocar rutas ni plantillas**.

### Estructura de directorios

```
manos-a-la-obra/
├── app.py                    # app factory, registra blueprint, /health
├── config.py                 # constantes (X_HANDLE), overridable por env
├── pyproject.toml            # uv: flask, pyyaml, gunicorn; dev: pytest
├── uv.lock
├── .python-version           # 3.13
├── nixpacks.toml             # build/deploy Railway
├── .env.example
├── .gitignore
├── CLAUDE.md
├── data/
│   └── contenido.yaml        # contenido curado (editar + push)
├── routes/
│   ├── __init__.py
│   └── paginas.py            # /, /impresion-3d, /puntos-acopio
├── services/
│   ├── __init__.py
│   └── contenido.py          # CAPA REPOSITORIO (seam para Fase 2)
├── templates/
│   ├── base.html             # Pico CSS + style.css
│   ├── index.html
│   ├── impresion_3d.html
│   └── puntos_acopio.html
├── static/
│   └── style.css
└── tests/
    ├── conftest.py
    ├── test_contenido.py     # lógica del repositorio (filtrado, mapa, archivo inválido)
    └── test_paginas.py       # smoke de rutas
```

## Modelo de datos (`data/contenido.yaml`)

Formato **YAML**, leído con `yaml.safe_load`. Estructura: dos listas de nivel superior.

```yaml
modelos_3d:
  - nombre: "Férula de antebrazo ajustable"
    descripcion: "Férula imprimible para inmovilización de antebrazo."
    url: "https://www.printables.com/model/..."
    material: "PLA o PETG"
    categoria: "férula"

puntos_acopio:
  - nombre: "Centro de acopio Chapinero"
    pais: "Colombia"
    ciudad: "Bogotá"
    direccion: "Calle 53 #13-20"
    recibe: "Agua, alimentos no perecederos, férulas impresas"
    horario: "8:00-18:00"
    contacto: "+57 300 000 0000"
    # mapa_url opcional; si falta, se genera desde direccion + ciudad + pais
```

**Campos de `modelos_3d`:** `nombre` (req), `url` (req), `descripcion` (opc),
`material` (opc), `categoria` (opc).

**Campos de `puntos_acopio`:** `nombre` (req), `pais` (req), `ciudad` (req),
`direccion` (req), `recibe` (opc), `horario` (opc), `contacto` (opc), `mapa_url` (opc).

**Link a Google Maps:** si `mapa_url` no se especifica, se genera con
`https://www.google.com/maps/search/?api=1&query=<urlencode(direccion, ciudad, pais)>`.

**Cuidado con YAML:** entrecomillar valores ambiguos (teléfonos `"+57 ..."`, horarios
`"8:00-18:00"`, y strings que YAML podría interpretar como booleano/número). El spec y el
CLAUDE.md documentarán esta convención.

### Interfaz del repositorio (`services/contenido.py`)

- `listar_modelos3d() -> list[dict]` — todos los modelos 3D.
- `listar_puntos(pais=None, ciudad=None) -> list[dict]` — puntos filtrados; cada dict
  incluye `mapa_url` ya resuelto (generado si faltaba).
- `opciones_filtro() -> dict` — `{"paises": [...], "ciudades": [...]}` (valores únicos
  ordenados) para poblar los `<select>` del filtro.

Comportamiento ante error: si `contenido.yaml` falta o está malformado, las funciones
devuelven listas/valores vacíos y registran una advertencia; **nunca lanzan excepción**
hacia las rutas. El archivo se lee en cada request (volumen de datos chico; simplicidad
sobre caché en el MVP).

## Rutas y páginas (`routes/paginas.py`)

- **`GET /`** → `index.html`. Título "Manos a la Obra", subtítulo, intro breve, dos accesos
  grandes a las secciones, y bloque **"¿Tenés info para aportar? Escribime en X →
  @davidfgonzalezc"**. Nota corta: la información es colaborativa, conviene verificar antes de actuar.
- **`GET /impresion-3d`** → `impresion_3d.html`. Lista de modelos: nombre, descripción,
  material, botón "Ver / Descargar" (link externo, `target="_blank" rel="noopener"`).
- **`GET /puntos-acopio`** → `puntos_acopio.html`. Filtro **país + ciudad** vía
  `<form method="get">` con dos `<select>` (opción "Todos") + botón; el servidor re-renderiza
  filtrado (sin JS, robusto en mala conexión). Lista con dirección, qué recibe, horario,
  contacto y "Ver en Google Maps". Estado vacío claro si el filtro no da resultados.
- **`GET /health`** → `{"status": "ok"}` (para health checks de Railway).

Estética con **Pico CSS** (CDN) + un `static/style.css` chico. Sin HTMX en el MVP.

## Manejo de errores y estados vacíos

- Contenido faltante/malformado → páginas renderizan estado vacío ("Aún no hay
  información cargada"), la app no cae, `/health` sigue en 200.
- Filtro sin resultados → mensaje "No hay puntos de acopio para ese filtro."
- Links externos abren en pestaña nueva con `rel="noopener"`.

## Deploy (Railway / Nixpacks)

`nixpacks.toml`:
```toml
[phases.setup]
nixPkgs = ["python313", "python313Packages.pip"]

[phases.install]
cmds = ["pip install ."]

[start]
cmd = "gunicorn 'app:create_app()' --bind 0.0.0.0:${PORT:-8080}"
```

- Servidor de producción **gunicorn** (no el dev server de Flask), usando la sintaxis de
  app factory `app:create_app()`.
- Bindeo a `0.0.0.0` y al `$PORT` que inyecta Railway (fallback `8080` en local).
- `uv.lock` commiteado para builds reproducibles.
- `X_HANDLE` en `config.py` con default `"davidfgonzalezc"`, overridable por variable de
  entorno. El MVP no necesita `SECRET_KEY` (no hay sesión ni formularios que la requieran).

## Testing (pytest, TDD)

- **`test_contenido.py`:** carga un YAML de muestra (archivo temporal); `listar_puntos`
  filtra correctamente por país, por ciudad, y por ambos; `mapa_url` se autogenera cuando
  falta y se respeta cuando viene dado; `listar_modelos3d` devuelve todos; archivo
  inexistente/malformado → listas vacías sin excepción; `opciones_filtro` devuelve valores
  únicos ordenados.
- **`test_paginas.py`:** `GET /` responde 200 y contiene el link a X; `GET /impresion-3d`
  y `GET /puntos-acopio` responden 200; el filtro por query params (`?pais=&ciudad=`)
  acota resultados; estados vacíos se renderizan sin error; `GET /health` responde 200.

## Fase 2 (documentada, no se construye ahora)

- **Postgres** en Railway (variable `DATABASE_URL`, driver `psycopg`).
- Nueva implementación del repositorio sobre DB, respetando la **misma interfaz** de
  `services/contenido.py`; rutas y plantillas quedan intactas.
- **`routes/enviar.py`:** formulario de envío anónimo (crea registros en estado "pendiente").
- **`routes/admin.py`** + login de admin (contraseña única): cola de moderación para
  aprobar/rechazar envíos.
- Migración: sembrar la DB con el contenido actual del YAML.

## Decisiones registradas

- Enfoque **A** (Flask + archivo versionado con capa repositorio), elegido sobre sitio
  estático puro y sobre Postgres-desde-el-día-uno, por calzar con el fasing (estático
  ahora, colaboración después) sin infraestructura prematura.
- Contenido en **YAML** (preferencia del mantenedor; adecuado para edición manual).
- Ubicación de puntos: **lista filtrable por país/ciudad** + link a Google Maps
  (sin mapa interactivo en el MVP).
- Handle de contacto: **@davidfgonzalezc** en X.
```
