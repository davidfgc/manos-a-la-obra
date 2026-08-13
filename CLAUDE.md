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

## Deploy (Railway)

- `railway.toml` (`[deploy] startCommand`) es la fuente de verdad del arranque:
  `gunicorn 'app:create_app()' --bind 0.0.0.0:${PORT:-8080}`. Railway lo respeta con
  cualquier builder y tiene prioridad sobre el comando autodetectado.
- Railway usa por defecto el builder **Railpack** (mise + uv), que **ignora `nixpacks.toml`**;
  ese archivo queda solo como fallback si se cambia el builder a Nixpacks. Sin `railway.toml`,
  Railpack autogenera `gunicorn main:app`, que falla con `No module named 'main'`.
- Endpoint de health: `/health`.
- El MVP no requiere variables de entorno obligatorias (`X_HANDLE` es opcional).

## Fase 2 (pendiente)

Postgres en Railway + formulario de envio anonimo + login de admin/moderacion,
reemplazando la implementacion de `services/contenido.py` tras la misma interfaz.
Ver `docs/superpowers/specs/2026-08-12-manos-a-la-obra-design.md`.
