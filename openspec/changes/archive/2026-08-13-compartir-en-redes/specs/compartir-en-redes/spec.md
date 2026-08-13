## Purpose

Define el comportamiento observable de la previsualización del sitio al compartirlo en redes sociales: qué metadatos expone cada página, cómo se construyen las URLs absolutas, y qué imagen de marca con llamado a la acción se muestra por sección.

## ADDED Requirements

### Requirement: Metadatos de compartir en todas las páginas

Cada página HTML DEBE incluir en el `<head>` los metadatos Open Graph `og:type`, `og:url`, `og:title`, `og:description`, `og:image`, `og:image:width` (1200), `og:image:height` (630), `og:site_name` y `og:locale`; y los metadatos Twitter `twitter:card` (con valor `summary_large_image`), `twitter:title`, `twitter:description` y `twitter:image`.

#### Scenario: La home expone los metadatos base
- **WHEN** se solicita `/`
- **THEN** el HTML incluye `og:title`, `og:description`, `og:image`, `og:url` y `twitter:card` con valor `summary_large_image`

#### Scenario: Dimensiones declaradas de la imagen
- **WHEN** se renderiza cualquier página
- **THEN** el HTML declara `og:image:width` = 1200 y `og:image:height` = 630

### Requirement: Contenido por sección con fallback a home

Las secciones home (`/`), impresión 3D (`/impresion-3d`) y puntos de acopio (`/puntos-acopio`) DEBEN exponer su propio `og:title`, `og:description` y `og:image`. Una página que no defina un valor propio DEBE usar el valor por defecto (el de home). El título y la descripción DEBEN estar redactados como llamado a la acción.

#### Scenario: Cada sección tiene su propio título
- **WHEN** se solicitan `/`, `/impresion-3d` y `/puntos-acopio`
- **THEN** cada respuesta tiene un `og:title` distinto y acorde a esa sección

#### Scenario: Cada sección apunta a su imagen
- **WHEN** se solicita `/impresion-3d`
- **THEN** su `og:image` apunta a la imagen de esa sección, distinta de la de home

#### Scenario: Fallback al valor por defecto
- **WHEN** una página no define `og:title`/`og:description`/`og:image` propios
- **THEN** usa los valores por defecto de home sin dejar el metadato vacío

### Requirement: URLs absolutas desde SITE_URL

`og:url` y `og:image` DEBEN ser URLs absolutas con esquema `https`, construidas a partir de un `SITE_URL` configurable (con valor por defecto y override por variable de entorno). `og:url` DEBE corresponder a la ruta de la página. La construcción NO DEBE producir barras duplicadas.

#### Scenario: og:image es absoluta
- **WHEN** se renderiza cualquier página
- **THEN** el valor de `og:image` empieza con `https://` y termina en la ruta del PNG de la sección

#### Scenario: og:url refleja la ruta
- **WHEN** se solicita `/puntos-acopio`
- **THEN** `og:url` es `SITE_URL` + `/puntos-acopio`, sin barras duplicadas

### Requirement: Imagen de previsualización por sección

Cada sección DEBE servir una imagen de previsualización de 1200×630 px en una ruta estable bajo `/static/og/`. La imagen DEBE ser acorde a la marca (paleta y wordmark del sitio) e incluir un texto de llamado a la acción legible.

#### Scenario: La imagen existe con las dimensiones correctas
- **WHEN** se solicita la imagen de una sección bajo `/static/og/`
- **THEN** la respuesta es una imagen de 1200×630 px

#### Scenario: El metadato apunta a una imagen existente
- **WHEN** se renderiza una sección
- **THEN** su `og:image` referencia un archivo que existe y se sirve con éxito

### Requirement: Favicon

El sitio DEBE declarar un favicon en el `<head>` y servirlo con éxito.

#### Scenario: Favicon declarado y servido
- **WHEN** se solicita cualquier página
- **THEN** el `<head>` incluye un `<link rel="icon">` cuyo recurso se sirve con éxito
