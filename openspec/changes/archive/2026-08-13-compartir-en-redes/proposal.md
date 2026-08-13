## Why

Cuando alguien comparte el link del sitio en WhatsApp, X o Facebook, hoy no aparece ninguna previsualización: el `<head>` no tiene metadatos Open Graph ni Twitter Card, ni una imagen. En una emergencia el link se difunde justamente por redes; una tarjeta con imagen de marca y un llamado a la acción claro aumenta los clics y, con eso, el alcance de la ayuda.

## What Changes

- **Metadatos Open Graph + Twitter Card** en el `<head>`, **por sección** (home, impresión 3D, puntos de acopio), cada una con su título, descripción e imagen, con *fallback* a los de home.
- **Imagen de previsualización 1200×630 por sección**, acorde a la marca (azul institucional, wordmark, acento de bandera/triage) y con un **CTA visible** dentro de la imagen.
- **`SITE_URL`** en config para construir URLs absolutas (`og:url`, `og:image`); por defecto el dominio de Railway (`https://manos-a-la-obra-production.up.railway.app`), con override por variable de entorno.
- **Favicon** (adyacente; hoy ausente).
- **Generador de imágenes sin navegador** (Pillow) como herramienta de desarrollo: los PNG se generan en local y se commitean; el runtime solo sirve archivos estáticos.

## Capabilities

### New Capabilities
- `compartir-en-redes`: previsualización enriquecida al compartir el sitio en redes sociales — metadatos Open Graph/Twitter por sección, imágenes de marca con CTA, URLs absolutas desde `SITE_URL` y favicon.

### Modified Capabilities
<!-- Ninguna: no cambia el comportamiento de capabilities existentes. -->

## Impact

- **Plantillas**: `templates/base.html` (bloques Jinja de metadatos OG/Twitter + favicon); `templates/index.html`, `impresion_3d.html`, `puntos_acopio.html` (definen su `og:*` por sección).
- **Config/app**: `config.py` (`SITE_URL`); `app.py` (context processor/globals para URL absoluta).
- **Estáticos nuevos**: `static/og/*.png`, `static/favicon.*` (versionados en el repo).
- **Herramienta de dev**: `tools/generar_og.py` + una fuente TTF libre bundleada; `Pillow` como dependencia de desarrollo (no de runtime).
- **Sin cambios** en `data/contenido.yaml`, `services/contenido.py` ni en las rutas de contenido. Compatible con la migración a Postgres de Fase 2 (esto vive en la capa de presentación).
