## 1. Config y URL absoluta

- [x] 1.1 Agregar `SITE_URL` en `config.py` (override por env `SITE_URL`, default `https://manos-a-la-obra-production.up.railway.app`).
- [x] 1.2 En `app.py`, exponer a las plantillas `site_url` y un helper para construir URL absoluta desde una ruta, normalizando la barra final (sin `//`).
- [x] 1.3 Tests: `og:url` es `SITE_URL` + ruta de la página, absoluto y sin barras duplicadas.

## 2. Metadatos en plantillas

- [x] 2.1 En `base.html`, definir bloques `og_title` / `og_description` / `og_image` con defaults (home) y renderizar `og:type/url/title/description/image` + `og:image:width`(1200)/`height`(630) + `og:site_name` + `og:locale` (es_CO) + `twitter:card=summary_large_image` / `twitter:title/description/image`, y el `<link rel="icon">`.
- [x] 2.2 En `index.html`, `impresion_3d.html` y `puntos_acopio.html`, sobrescribir los bloques con el copy por sección (título/descripción como llamado a la acción) y su `og:image`.
- [x] 2.3 Tests: cada sección tiene su `og:title` propio; `twitter:card=summary_large_image`; `og:image` absoluta apuntando al PNG de esa sección; una página sin override usa el default de home.

## 3. Generador de imágenes (dev, sin navegador)

- [x] 3.1 Bundlear una fuente TTF libre en el repo (p. ej. bajo `tools/assets/`) y agregar `Pillow` como dependencia de **desarrollo** (no de runtime).
- [x] 3.2 Crear `tools/generar_og.py`: una plantilla 1200×630 parametrizada por sección (fondo de marca, wordmark, headline/CTA, franja de bandera, acento por sección) que escribe `static/og/home.png`, `static/og/impresion.png`, `static/og/puntos.png`.
- [x] 3.3 Generar el favicon (`static/favicon.png` o `.svg`) — con el mismo tool o como estático simple.
- [x] 3.4 Ejecutar el generador y **commitear** los PNG y el favicon.

## 4. Verificación

- [x] 4.1 Ejecutar `uv run pytest` (incluye los tests de metadatos e imágenes).
- [x] 4.2 Comprobar que cada PNG es 1200×630 y pesa < ~300 KB.
- [ ] 4.3 Tras desplegar, validar el unfurl con X Card Validator, Facebook Sharing Debugger y LinkedIn Post Inspector sobre la URL de Railway; anotar el caché de WhatsApp (`?v=` para forzar refresh). (Manual post-deploy.)
- [x] 4.4 Ejecutar `openspec validate compartir-en-redes` y corregir lo que reporte.
