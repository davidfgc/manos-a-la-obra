## Why

La página de inicio ya invita a colaborar por X, pero la ayuda se está organizando también en comunidades (grupos de WhatsApp de makers, voluntarios, etc.). Hoy no hay dónde listarlas, así que quien llega no encuentra por dónde sumarse a esos grupos. Empezamos con uno ("Makers unidos por Colombia") y la lista debe poder crecer sin tocar código.

## What Changes

- La home muestra una nueva sección **"Otros grupos"** ubicada **después** del bloque de contacto por X.
- La sección lista grupos/comunidades externas: cada uno con su **nombre** como enlace que abre en pestaña nueva (`target="_blank"`, `rel="noopener"`).
- Contenido inicial: **"Makers unidos por Colombia"** → enlace al grupo de WhatsApp.
- Los grupos son **contenido curado en `data/contenido.yaml`** (nueva clave `grupos`), servidos por la capa repositorio como el resto del contenido; el mantenedor agrega grupos editando el YAML, sin tocar plantillas.
- Si no hay grupos cargados, la sección no se muestra (sin estado vacío ruidoso).

## Capabilities

### New Capabilities
- `grupos`: directorio curado de grupos/comunidades externas de ayuda mostrado en la página de inicio.

### Modified Capabilities
<!-- Ninguna. -->

## Impact

- **Contenido**: `data/contenido.yaml` — nueva clave opcional `grupos` (lista de `{nombre, url}`).
- **Repositorio**: `services/contenido.py` — nueva función `listar_grupos()` (misma interfaz de solo lectura que `listar_modelos3d`/`listar_puntos`).
- **Ruta**: `routes/paginas.py` — `index()` pasa `grupos` a la plantilla.
- **Plantilla**: `templates/index.html` — sección "Otros grupos" tras el bloque de X.
- Sin dependencias nuevas, sin variables de entorno, sin cambios de rutas. Compatible con la migración a Postgres de Fase 2 (los grupos viven tras la interfaz del repositorio).
