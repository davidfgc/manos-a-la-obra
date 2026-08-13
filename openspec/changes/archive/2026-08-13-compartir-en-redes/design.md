## Context

Ver `proposal.md` (Why). Estado actual:

- `templates/base.html` tiene un `<head>` mínimo (charset, viewport, `title`, `style.css`). Sin OG/Twitter, sin favicon.
- Las rutas (`routes/paginas.py`) son delgadas y el modelo de datos vive detrás de `services/contenido.py`; este cambio NO debe engrosar rutas ni tocar datos.
- `config.py` ya establece el patrón de config por entorno (`X_HANDLE`). No hay noción de dominio propio en el código.
- Despliegue en Railway (gunicorn); dominio actual `https://manos-a-la-obra-production.up.railway.app`.
- Principio del proyecto: *carga ligera / resiliente en redes lentas*. Ya existe un sistema de diseño con tokens (azul `#0F4C81`, triage, wordmark "Manos a la Obra").

## Goals / Non-Goals

**Goals:**
- Previsualización rica y **por sección** al compartir, sin tocar el modelo de datos ni las rutas de contenido.
- Runtime liviano: servir **PNG estáticos**; ninguna dependencia de generación en el runtime de Railway.
- Generación **determinista y sin navegador**.

**Non-Goals:**
- OG cards **dinámicas por-necesidad** o con datos en vivo (Fase 2; además el caché de scrapers las volvería ilusorias).
- Internacionalización de metadatos más allá de español.
- Invalidación automática del caché de los scrapers.

## Decisions

### 1. Generación en build-time (local), no en request-time
Un generador local produce los PNG y se **commitean** en `static/og/`. Railway solo sirve estáticos.

*Por qué:* los scrapers cachean la preview, así que una imagen "viva" en cada request es una ilusión; y evita CPU, cold starts y dependencias pesadas en runtime (coherente con *carga ligera*). *Alternativa descartada:* endpoint dinámico `/og/<seccion>.png`.

### 2. Dibujo con Pillow + fuente TTF bundleada (sin navegador)
La card es **tipográfica + acento** (fondo de marca, wordmark, headline/CTA, franja de bandera; acento por sección tomado de la paleta de triage). Se usa **Pillow** con una **fuente TTF libre incluida en el repo**.

*Por qué:* sin navegador, liviano y **determinista** (no depende de fuentes del sistema, que difieren entre tu máquina y CI/Linux). *Alternativas consideradas:* SVG→PNG (cairo/pango: fuentes finicky, libs de sistema) y HTML→PNG (máxima fidelidad pero exige un navegador). El glifo del corazón queda **diferido** (rasterizarlo sin navegador es lo único incómodo y no aporta al MVP).

### 3. Metadatos por sección con bloques Jinja (rutas intactas)
`base.html` define bloques `og_title` / `og_description` / `og_image` con **valores por defecto (home)** y renderiza los `og:*` / `twitter:*`. Cada plantilla de página **sobrescribe** esos bloques con su copy.

*Por qué:* mantiene las rutas delgadas (el texto vive con la vista) y da fallback natural. *Alternativa:* pasar el copy desde las rutas o un context processor con un mapa `ruta→meta` (descartado por acoplar rutas/estado a algo puramente de presentación).

### 4. URL absoluta desde `SITE_URL` (config), no `_external`
`config.py` expone `SITE_URL` (default = dominio de Railway; override por env). `app.py` inyecta `site_url` y un helper para componer `og:url`/`og:image` **normalizando la barra final**.

*Por qué:* Railway está detrás de proxy; `url_for(_external=True)` puede emitir esquema/host equivocados salvo con ProxyFix. Un `SITE_URL` explícito es predecible y sin sorpresas. Sin variable de entorno obligatoria (hay default).

### 5. Pillow como dependencia de **desarrollo**, no de runtime
El generador y su fuente viven en el repo; los PNG resultantes también. Railway **no** instala Pillow.

*Por qué:* el runtime se mantiene mínimo; la generación es una tarea de mantenedor (como curar el YAML). *Compat:* `gunicorn 'app:create_app()'` no cambia.

## Risks / Trade-offs

- **Fuente no determinista** → Mitigación: bundlear una TTF libre y referenciarla explícitamente; no usar fuentes del sistema.
- **Peso del PNG** (WhatsApp muestra confiable < ~300 KB) → Mitigación: fondo plano de marca, exportar optimizado a 1200×630.
- **Caché de scrapers** al actualizar arte/copy → Mitigación: documentar validadores (X Card Validator, FB Sharing Debugger, LinkedIn Post Inspector) y el truco `?v=` para WhatsApp.
- **Deriva copy/imagen ↔ contenido** → Mitigación: el copy de cada sección se define en un solo lugar reutilizado por plantilla y generador.
- **Dominio propio a futuro** → `SITE_URL` es config; cambiar el default o la env basta, sin tocar plantillas.

## Migration Plan

Cambio aditivo y de presentación. Deploy = push (Railway sirve los nuevos estáticos). Rollback = revertir el commit (los metadatos y estáticos desaparecen sin afectar contenido). Regenerar imágenes = correr `tools/generar_og.py` y commitear. Sin variables de entorno obligatorias (`SITE_URL` tiene default).

## Open Questions

- ¿Se migrará a un dominio propio? No cambia el diseño (solo el default/env de `SITE_URL`), así que puede resolverse después.
