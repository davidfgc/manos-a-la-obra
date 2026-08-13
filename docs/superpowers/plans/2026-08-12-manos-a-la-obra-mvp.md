# Manos a la Obra — MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sitio Flask de solo lectura que centraliza archivos 3D imprimibles y puntos de acopio (filtrables por país/ciudad) para la ayuda del terremoto en Colombia, desplegable en Railway.

**Architecture:** App factory de Flask + Jinja2 + Pico CSS. El contenido se cura en un archivo YAML versionado y se lee a través de una capa repositorio (`services/contenido.py`) con interfaz estable; en Fase 2 esa capa se reemplaza por Postgres sin tocar rutas ni plantillas. Sin base de datos, sesión ni autenticación en el MVP.

**Tech Stack:** Python 3.13 · Flask · PyYAML · gunicorn (producción) · pytest · uv · Nixpacks (Railway).

**Spec:** `docs/superpowers/specs/2026-08-12-manos-a-la-obra-design.md`

## Global Constraints

- **Python:** `>=3.13` (`.python-version` = `3.13`).
- **Dependencias:** `flask>=3.1`, `pyyaml>=6.0`, `gunicorn>=23.0`; dev: `pytest>=8.0`.
- **Solo español** en todo el texto de UI. Sin i18n.
- **Sin** base de datos, sesión, `SECRET_KEY`, autenticación ni formularios de escritura en el MVP.
- **YAML:** leer siempre con `yaml.safe_load`. Convención: entrecomillar valores ambiguos (teléfonos, horarios, strings tipo "no"/"sí").
- **Handle de X:** default `"davidfgonzalezc"`, overridable por env `X_HANDLE`. Se muestra como `@{{ x_handle }}` enlazando a `https://x.com/{{ x_handle }}`.
- **Comando de arranque en producción:** `gunicorn 'app:create_app()' --bind 0.0.0.0:${PORT:-8080}`.
- **Links externos:** siempre `target="_blank" rel="noopener"`.
- **Commits:** Conventional Commits; cada commit termina con el trailer `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Todos los comandos se corren desde la raíz del repo con `uv run ...`.

---

### Task 1: Scaffolding del proyecto y tooling

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `nixpacks.toml`

**Interfaces:**
- Consumes: nada.
- Produces: entorno `uv` instalable; `uv run pytest` disponible; raíz del repo en `pythonpath` para importar `app`, `config`, `services`, `routes`.

- [ ] **Step 1: Crear `.python-version`**

```
3.13
```

- [ ] **Step 2: Crear `pyproject.toml`**

```toml
[project]
name = "manos-a-la-obra"
version = "0.1.0"
description = "Centralizacion de informacion de ayuda para el terremoto en Colombia"
requires-python = ">=3.13"
dependencies = [
    "flask>=3.1",
    "pyyaml>=6.0",
    "gunicorn>=23.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 3: Crear `.gitignore`**

```
.venv/
__pycache__/
*.pyc
.env
```

- [ ] **Step 4: Crear `.env.example`**

```
# El MVP no requiere variables obligatorias.
# Opcional: sobreescribir el handle de X mostrado en el sitio.
# X_HANDLE=davidfgonzalezc
```

- [ ] **Step 5: Crear `nixpacks.toml`**

```toml
[phases.setup]
nixPkgs = ["python313", "python313Packages.pip"]

[phases.install]
cmds = ["pip install ."]

[start]
cmd = "gunicorn 'app:create_app()' --bind 0.0.0.0:${PORT:-8080}"
```

- [ ] **Step 6: Instalar dependencias**

Run: `uv sync`
Expected: crea `.venv/` y `uv.lock`, instala flask, pyyaml, gunicorn, pytest sin errores.

- [ ] **Step 7: Verificar que las dependencias importan**

Run: `uv run python -c "import flask, yaml, gunicorn; print('ok')"`
Expected: imprime `ok`.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml uv.lock .python-version .gitignore .env.example nixpacks.toml
git commit -m "chore: scaffold flask project with uv and nixpacks"
```

---

### Task 2: Capa repositorio de contenido (`services/contenido.py`)

**Files:**
- Create: `services/__init__.py`
- Create: `services/contenido.py`
- Test: `tests/test_contenido.py`

**Interfaces:**
- Consumes: nada (lógica pura + PyYAML).
- Produces:
  - `services.contenido.DATA_PATH: pathlib.Path` — ruta por defecto a `data/contenido.yaml`.
  - `listar_modelos3d(*, path=DATA_PATH) -> list[dict]`
  - `listar_puntos(pais=None, ciudad=None, *, path=DATA_PATH) -> list[dict]` — cada dict incluye `mapa_url` resuelto.
  - `opciones_filtro(*, path=DATA_PATH) -> dict` con claves `"paises"` y `"ciudades"` (listas de str únicas ordenadas).
  - Ante archivo inexistente/malformado, todas devuelven vacío sin lanzar excepción.

- [ ] **Step 1: Crear `services/__init__.py`** (vacío)

```python
```

- [ ] **Step 2: Escribir los tests que fallan (`tests/test_contenido.py`)**

```python
import textwrap
from services import contenido


def _escribir_yaml(tmp_path, texto):
    p = tmp_path / "contenido.yaml"
    p.write_text(textwrap.dedent(texto), encoding="utf-8")
    return p


def test_listar_modelos3d_devuelve_todos(tmp_path):
    p = _escribir_yaml(tmp_path, """
        modelos_3d:
          - nombre: "Ferula A"
            url: "https://ejemplo/a"
          - nombre: "Ferula B"
            url: "https://ejemplo/b"
    """)
    modelos = contenido.listar_modelos3d(path=p)
    assert [m["nombre"] for m in modelos] == ["Ferula A", "Ferula B"]


def test_listar_puntos_filtra_por_pais_y_ciudad(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - nombre: "P1"
            pais: "Colombia"
            ciudad: "Bogota"
            direccion: "Calle 1"
          - nombre: "P2"
            pais: "Colombia"
            ciudad: "Medellin"
            direccion: "Calle 2"
          - nombre: "P3"
            pais: "Ecuador"
            ciudad: "Quito"
            direccion: "Calle 3"
    """)
    assert [x["nombre"] for x in contenido.listar_puntos(path=p)] == ["P1", "P2", "P3"]
    assert [x["nombre"] for x in contenido.listar_puntos(pais="Colombia", path=p)] == ["P1", "P2"]
    assert [x["nombre"] for x in contenido.listar_puntos(pais="Colombia", ciudad="Bogota", path=p)] == ["P1"]


def test_mapa_url_se_genera_cuando_falta(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - nombre: "P1"
            pais: "Colombia"
            ciudad: "Bogota"
            direccion: "Calle 53 13-20"
    """)
    punto = contenido.listar_puntos(path=p)[0]
    assert punto["mapa_url"].startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "Calle" in punto["mapa_url"]


def test_mapa_url_respeta_override(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - nombre: "P1"
            pais: "Colombia"
            ciudad: "Bogota"
            direccion: "Calle 1"
            mapa_url: "https://maps.example/p1"
    """)
    assert contenido.listar_puntos(path=p)[0]["mapa_url"] == "https://maps.example/p1"


def test_opciones_filtro_valores_unicos_ordenados(tmp_path):
    p = _escribir_yaml(tmp_path, """
        puntos_acopio:
          - {nombre: P1, pais: Colombia, ciudad: Medellin, direccion: c1}
          - {nombre: P2, pais: Colombia, ciudad: Bogota, direccion: c2}
          - {nombre: P3, pais: Ecuador, ciudad: Quito, direccion: c3}
    """)
    opciones = contenido.opciones_filtro(path=p)
    assert opciones["paises"] == ["Colombia", "Ecuador"]
    assert opciones["ciudades"] == ["Bogota", "Medellin", "Quito"]


def test_archivo_inexistente_devuelve_vacio(tmp_path):
    faltante = tmp_path / "no_existe.yaml"
    assert contenido.listar_modelos3d(path=faltante) == []
    assert contenido.listar_puntos(path=faltante) == []
    assert contenido.opciones_filtro(path=faltante) == {"paises": [], "ciudades": []}
```

- [ ] **Step 3: Correr los tests para verificar que fallan**

Run: `uv run pytest tests/test_contenido.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'services.contenido'`.

- [ ] **Step 4: Implementar `services/contenido.py`**

```python
import logging
import urllib.parse
from pathlib import Path

import yaml

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "contenido.yaml"


def _cargar(path=DATA_PATH):
    """Carga el YAML de contenido. Devuelve {} si falta o esta malformado."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    except yaml.YAMLError:
        logging.warning("contenido.yaml malformado: %s", path)
        return {}
    return data if isinstance(data, dict) else {}


def _mapa_url(punto):
    if punto.get("mapa_url"):
        return punto["mapa_url"]
    partes = [punto.get("direccion"), punto.get("ciudad"), punto.get("pais")]
    query = ", ".join(str(p) for p in partes if p)
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote_plus(query)


def listar_modelos3d(*, path=DATA_PATH):
    return list(_cargar(path).get("modelos_3d") or [])


def listar_puntos(pais=None, ciudad=None, *, path=DATA_PATH):
    puntos = _cargar(path).get("puntos_acopio") or []
    resultado = []
    for p in puntos:
        if pais and p.get("pais") != pais:
            continue
        if ciudad and p.get("ciudad") != ciudad:
            continue
        punto = dict(p)
        punto["mapa_url"] = _mapa_url(p)
        resultado.append(punto)
    return resultado


def opciones_filtro(*, path=DATA_PATH):
    puntos = _cargar(path).get("puntos_acopio") or []
    paises = sorted({p.get("pais") for p in puntos if p.get("pais")})
    ciudades = sorted({p.get("ciudad") for p in puntos if p.get("ciudad")})
    return {"paises": paises, "ciudades": ciudades}
```

- [ ] **Step 5: Correr los tests para verificar que pasan**

Run: `uv run pytest tests/test_contenido.py -v`
Expected: PASS (7 tests).

- [ ] **Step 6: Commit**

```bash
git add services/__init__.py services/contenido.py tests/test_contenido.py
git commit -m "feat(contenido): add YAML content repository with filtering"
```

---

### Task 3: App factory, config y health check

**Files:**
- Create: `config.py`
- Create: `app.py`
- Create: `tests/conftest.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: nada.
- Produces:
  - `config.X_HANDLE: str` — handle de X (default `"davidfgonzalezc"`, env `X_HANDLE`).
  - `app.create_app() -> flask.Flask` — expone `/health`; inyecta `x_handle` en el contexto de plantillas.
  - Fixtures pytest `app` y `client` en `tests/conftest.py`.

- [ ] **Step 1: Crear `config.py`**

```python
import os

X_HANDLE = os.environ.get("X_HANDLE", "davidfgonzalezc")
```

- [ ] **Step 2: Crear `tests/conftest.py`**

```python
import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()
```

- [ ] **Step 3: Escribir el test que falla (`tests/test_app.py`)**

```python
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
```

- [ ] **Step 4: Correr el test para verificar que falla**

Run: `uv run pytest tests/test_app.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'app'`.

- [ ] **Step 5: Implementar `app.py`**

```python
from flask import Flask, jsonify

from config import X_HANDLE


def create_app():
    app = Flask(__name__)

    @app.context_processor
    def inject_globals():
        return {"x_handle": X_HANDLE}

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
```

- [ ] **Step 6: Correr el test para verificar que pasa**

Run: `uv run pytest tests/test_app.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add config.py app.py tests/conftest.py tests/test_app.py
git commit -m "feat(app): add flask app factory with health check"
```

---

### Task 4: Layout base y página de inicio

**Files:**
- Create: `routes/__init__.py`
- Create: `routes/paginas.py`
- Modify: `app.py` (registrar el blueprint)
- Create: `templates/base.html`
- Create: `templates/index.html`
- Create: `static/style.css`
- Test: `tests/test_paginas.py`

**Interfaces:**
- Consumes: `app.create_app()`, `config.X_HANDLE` (vía `x_handle` en plantillas).
- Produces:
  - `routes.paginas.paginas_bp: flask.Blueprint` con la ruta `GET /` → `index.html`.
  - `templates/base.html` con bloques `title` y `content`.

- [ ] **Step 1: Crear `routes/__init__.py`** (vacío)

```python
```

- [ ] **Step 2: Escribir el test que falla (`tests/test_paginas.py`)**

```python
def test_home_ok_y_muestra_handle(client):
    resp = client.get("/")
    assert resp.status_code == 200
    cuerpo = resp.get_data(as_text=True)
    assert "Manos a la Obra" in cuerpo
    assert "x.com/davidfgonzalezc" in cuerpo
```

- [ ] **Step 3: Correr el test para verificar que falla**

Run: `uv run pytest tests/test_paginas.py -v`
Expected: FAIL con status 404 (la ruta `/` no existe todavía).

- [ ] **Step 4: Crear `routes/paginas.py`**

```python
from flask import Blueprint, render_template

paginas_bp = Blueprint("paginas", __name__)


@paginas_bp.route("/")
def index():
    return render_template("index.html")
```

- [ ] **Step 5: Registrar el blueprint en `app.py`**

Añadir, dentro de `create_app()` justo antes de `return app`:

```python
    from routes.paginas import paginas_bp

    app.register_blueprint(paginas_bp)
```

- [ ] **Step 6: Crear `static/style.css`**

```css
:root { --pico-font-family: system-ui, -apple-system, sans-serif; }
main.container { padding-block: 2rem; }
article { margin-block-end: 1rem; }
```

- [ ] **Step 7: Crear `templates/base.html`**

```html
<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Manos a la Obra{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <nav class="container">
    <ul><li><strong><a href="/">Manos a la Obra</a></strong></li></ul>
    <ul>
      <li><a href="/impresion-3d">Impresion 3D</a></li>
      <li><a href="/puntos-acopio">Puntos de acopio</a></li>
    </ul>
  </nav>
  <main class="container">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

- [ ] **Step 8: Crear `templates/index.html`**

```html
{% extends "base.html" %}
{% block content %}
<hgroup>
  <h1>Manos a la Obra</h1>
  <p>Informacion centralizada de ayuda para el terremoto en Colombia.</p>
</hgroup>

<div class="grid">
  <article>
    <h2>Archivos 3D para imprimir</h2>
    <p>Modelos imprimibles como ferulas y piezas de ayuda.</p>
    <a href="/impresion-3d" role="button">Ver archivos 3D</a>
  </article>
  <article>
    <h2>Puntos de acopio</h2>
    <p>Lugares que reciben donaciones, filtrables por pais y ciudad.</p>
    <a href="/puntos-acopio" role="button">Ver puntos de acopio</a>
  </article>
</div>

<article>
  <h3>Tenes informacion para aportar?</h3>
  <p>Escribime en X:
    <a href="https://x.com/{{ x_handle }}" target="_blank" rel="noopener">@{{ x_handle }}</a>.
    Reviso y agrego la informacion al sitio.</p>
  <small>La informacion es colaborativa; verifica antes de actuar.</small>
</article>
{% endblock %}
```

- [ ] **Step 9: Correr el test para verificar que pasa**

Run: `uv run pytest tests/test_paginas.py -v`
Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add routes/__init__.py routes/paginas.py app.py templates/base.html templates/index.html static/style.css tests/test_paginas.py
git commit -m "feat(paginas): add base layout and home page"
```

---

### Task 5: Contenido semilla y página de impresión 3D

**Files:**
- Create: `data/contenido.yaml`
- Modify: `routes/paginas.py` (añadir ruta `/impresion-3d`)
- Create: `templates/impresion_3d.html`
- Modify: `tests/test_paginas.py` (añadir test)

**Interfaces:**
- Consumes: `services.contenido.listar_modelos3d()`.
- Produces: ruta `GET /impresion-3d` → `impresion_3d.html`; archivo `data/contenido.yaml` con secciones `modelos_3d` y `puntos_acopio` (esta última la usa la Task 6).

- [ ] **Step 1: Crear `data/contenido.yaml` con contenido de ejemplo**

```yaml
# Contenido curado del sitio. Editar y hacer push para publicar.
# Entrecomillar valores ambiguos (telefonos, horarios).

modelos_3d:
  - nombre: "Ferula de dedo (ejemplo)"
    descripcion: "Modelo de ejemplo. Reemplazar con un enlace real verificado."
    url: "https://www.printables.com/"
    material: "PLA o PETG"
    categoria: "ferula"

puntos_acopio:
  - nombre: "Punto de acopio (ejemplo)"
    pais: "Colombia"
    ciudad: "Bogota"
    direccion: "Direccion de ejemplo 123"
    recibe: "Agua, alimentos no perecederos, insumos medicos"
    horario: "8:00-18:00"
    contacto: "Reemplazar con contacto real"
```

- [ ] **Step 2: Escribir el test que falla (añadir a `tests/test_paginas.py`)**

```python
def test_impresion_3d_ok_lista_modelos(client):
    resp = client.get("/impresion-3d")
    assert resp.status_code == 200
    cuerpo = resp.get_data(as_text=True)
    assert "Archivos 3D para imprimir" in cuerpo
    assert "Ferula de dedo (ejemplo)" in cuerpo
```

- [ ] **Step 3: Correr el test para verificar que falla**

Run: `uv run pytest tests/test_paginas.py::test_impresion_3d_ok_lista_modelos -v`
Expected: FAIL con status 404.

- [ ] **Step 4: Añadir la ruta en `routes/paginas.py`**

Añadir el import y la ruta:

```python
from services import contenido
```

```python
@paginas_bp.route("/impresion-3d")
def impresion_3d():
    modelos = contenido.listar_modelos3d()
    return render_template("impresion_3d.html", modelos=modelos)
```

- [ ] **Step 5: Crear `templates/impresion_3d.html`**

```html
{% extends "base.html" %}
{% block title %}Impresion 3D - Manos a la Obra{% endblock %}
{% block content %}
<h1>Archivos 3D para imprimir</h1>
{% if modelos %}
  {% for m in modelos %}
  <article>
    <h3>{{ m.nombre }}</h3>
    {% if m.descripcion %}<p>{{ m.descripcion }}</p>{% endif %}
    {% if m.material %}<p><small>Material: {{ m.material }}</small></p>{% endif %}
    <a href="{{ m.url }}" target="_blank" rel="noopener" role="button">Ver / Descargar</a>
  </article>
  {% endfor %}
{% else %}
  <p>Aun no hay archivos cargados.</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 6: Correr el test para verificar que pasa**

Run: `uv run pytest tests/test_paginas.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add data/contenido.yaml routes/paginas.py templates/impresion_3d.html tests/test_paginas.py
git commit -m "feat(paginas): add 3D printing page with seed content"
```

---

### Task 6: Página de puntos de acopio con filtro

**Files:**
- Modify: `routes/paginas.py` (añadir ruta `/puntos-acopio`)
- Create: `templates/puntos_acopio.html`
- Modify: `tests/test_paginas.py` (añadir tests)

**Interfaces:**
- Consumes: `services.contenido.listar_puntos(pais, ciudad)`, `services.contenido.opciones_filtro()`.
- Produces: ruta `GET /puntos-acopio` con query params opcionales `pais` y `ciudad`.

- [ ] **Step 1: Escribir los tests que fallan (añadir a `tests/test_paginas.py`)**

```python
def test_puntos_ok(client):
    resp = client.get("/puntos-acopio")
    assert resp.status_code == 200
    assert "Puntos de acopio" in resp.get_data(as_text=True)


def test_puntos_filtro_sin_resultados(client):
    resp = client.get("/puntos-acopio?pais=Narnia")
    assert resp.status_code == 200
    assert "No hay puntos de acopio para ese filtro." in resp.get_data(as_text=True)
```

- [ ] **Step 2: Correr los tests para verificar que fallan**

Run: `uv run pytest tests/test_paginas.py::test_puntos_ok tests/test_paginas.py::test_puntos_filtro_sin_resultados -v`
Expected: FAIL con status 404.

- [ ] **Step 3: Añadir la ruta en `routes/paginas.py`**

Añadir `request` al import de flask (`from flask import Blueprint, render_template, request`) y la ruta:

```python
@paginas_bp.route("/puntos-acopio")
def puntos_acopio():
    pais = request.args.get("pais") or None
    ciudad = request.args.get("ciudad") or None
    puntos = contenido.listar_puntos(pais=pais, ciudad=ciudad)
    opciones = contenido.opciones_filtro()
    return render_template(
        "puntos_acopio.html",
        puntos=puntos,
        opciones=opciones,
        pais=pais,
        ciudad=ciudad,
    )
```

- [ ] **Step 4: Crear `templates/puntos_acopio.html`**

```html
{% extends "base.html" %}
{% block title %}Puntos de acopio - Manos a la Obra{% endblock %}
{% block content %}
<h1>Puntos de acopio</h1>

<form method="get">
  <div class="grid">
    <select name="pais" aria-label="Pais">
      <option value="">Todos los paises</option>
      {% for p in opciones.paises %}
      <option value="{{ p }}" {% if p == pais %}selected{% endif %}>{{ p }}</option>
      {% endfor %}
    </select>
    <select name="ciudad" aria-label="Ciudad">
      <option value="">Todas las ciudades</option>
      {% for c in opciones.ciudades %}
      <option value="{{ c }}" {% if c == ciudad %}selected{% endif %}>{{ c }}</option>
      {% endfor %}
    </select>
    <button type="submit">Filtrar</button>
  </div>
</form>

{% if puntos %}
  {% for pt in puntos %}
  <article>
    <h3>{{ pt.nombre }}</h3>
    <p>{{ pt.direccion }}{% if pt.ciudad %}, {{ pt.ciudad }}{% endif %}{% if pt.pais %}, {{ pt.pais }}{% endif %}</p>
    {% if pt.recibe %}<p><strong>Recibe:</strong> {{ pt.recibe }}</p>{% endif %}
    {% if pt.horario %}<p><small>Horario: {{ pt.horario }}</small></p>{% endif %}
    {% if pt.contacto %}<p><small>Contacto: {{ pt.contacto }}</small></p>{% endif %}
    <a href="{{ pt.mapa_url }}" target="_blank" rel="noopener" role="button">Ver en Google Maps</a>
  </article>
  {% endfor %}
{% else %}
  <p>No hay puntos de acopio para ese filtro.</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Correr los tests para verificar que pasan**

Run: `uv run pytest tests/test_paginas.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add routes/paginas.py templates/puntos_acopio.html tests/test_paginas.py
git commit -m "feat(paginas): add collection points page with country/city filter"
```

---

### Task 7: Documentación, verificación final y guía de deploy

**Files:**
- Create: `CLAUDE.md`

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: `CLAUDE.md` con comandos, arquitectura y notas de deploy; suite completa verde; sitio verificado localmente.

- [ ] **Step 1: Crear `CLAUDE.md`**

```markdown
# CLAUDE.md

Guia para Claude Code en este repositorio.

## Que es

"Manos a la Obra": sitio Flask de solo lectura que centraliza informacion de ayuda
para el terremoto en Colombia (archivos 3D imprimibles y puntos de acopio filtrables
por pais/ciudad). El contenido lo cura el mantenedor editando `data/contenido.yaml`.

## Comandos

    uv sync                       # instalar dependencias
    uv run flask --app app run --debug   # dev server
    uv run pytest                 # tests
    uv run pytest tests/test_x.py -k "nombre"   # un solo test

## Arquitectura

- `app.py` - app factory `create_app()`, `/health`, inyecta `x_handle`.
- `config.py` - `X_HANDLE` (env override).
- `routes/paginas.py` - rutas: `/`, `/impresion-3d`, `/puntos-acopio`.
- `services/contenido.py` - CAPA REPOSITORIO. Lee `data/contenido.yaml`. Unica pieza
  que conoce el origen de los datos; en Fase 2 se reemplaza por Postgres sin tocar
  rutas ni plantillas. Interfaz: `listar_modelos3d()`, `listar_puntos(pais, ciudad)`,
  `opciones_filtro()`.
- `data/contenido.yaml` - contenido curado. Editar y hacer push para publicar.
  Entrecomillar valores ambiguos (telefonos, horarios).
- `templates/` - Jinja2 + Pico CSS (CDN). `static/style.css` para overrides.

## Deploy (Railway / Nixpacks)

- `nixpacks.toml` arranca gunicorn con la app factory, bindeado a `0.0.0.0:$PORT`.
- Endpoint de health: `/health`.
- El MVP no requiere variables de entorno obligatorias (`X_HANDLE` es opcional).

## Fase 2 (pendiente)

Postgres en Railway + formulario de envio anonimo + login de admin/moderacion,
reemplazando la implementacion de `services/contenido.py` tras la misma interfaz.
Ver `docs/superpowers/specs/2026-08-12-manos-a-la-obra-design.md`.
```

- [ ] **Step 2: Correr la suite completa**

Run: `uv run pytest -v`
Expected: PASS (todos los tests de `test_contenido.py`, `test_app.py`, `test_paginas.py`).

- [ ] **Step 3: Verificación manual del sitio**

Run: `uv run flask --app app run --debug`
Luego abrir `http://localhost:5000/` y comprobar: home con las dos tarjetas y el link a X;
`/impresion-3d` muestra el modelo de ejemplo; `/puntos-acopio` muestra el filtro y el punto
de ejemplo; el filtro por país/ciudad acota resultados; "Ver en Google Maps" abre la ubicación.
Detener con Ctrl-C.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md with commands, architecture and deploy notes"
```

- [ ] **Step 5 (manual, fuera de código): Deploy en Railway**

1. Subir el repo a GitHub (`git remote add origin ... && git push -u origin main`).
2. En Railway: New Project → Deploy from GitHub repo → seleccionar el repo.
3. Railway detecta `nixpacks.toml` y construye automáticamente.
4. Verificar que responde en `/health` y que las tres páginas cargan.
5. (Opcional) Configurar un dominio y la variable `X_HANDLE` si difiere del default.

---

## Notas de ejecución

- TDD estricto: test que falla → implementación mínima → test que pasa → commit.
- Correr `uv run pytest` antes de cada commit de código.
- No introducir base de datos, sesión ni dependencias fuera de las declaradas en Global Constraints.
