## 1. Contenido de ejemplo

- [x] 1.1 En `data/contenido.yaml`, ampliar los modelos de `modelos_3d` con los campos nuevos opcionales (`prioridad`, `destinatario`, `tamano`, `ciudades`, `cubierto`) y añadir 2-3 modelos de ejemplo que cubran: varias prioridades, ambos destinatarios, distintos tamaños, un modelo multi-ciudad, un modelo sin ciudades (general) y uno marcado `cubierto: true`.
- [x] 1.2 Añadir comentario en el YAML documentando los valores válidos (`prioridad: alta|media|baja`, `tamano: pequeno|mediano|grande`, `ciudades: [lista]`, `cubierto: true|false`).

## 2. Repositorio (`services/contenido.py`) — TDD

- [x] 2.1 Escribir tests (en `tests/`) para el orden por prioridad: `alta` antes que `media` antes que `baja`, y desempate estable por orden de contenido; prioridad ausente se trata como `media`.
- [x] 2.2 Escribir tests para la separación de cubiertos: `listar_modelos3d()` devuelve `{"activos": [...], "cubiertos": [...]}` con los cubiertos fuera de `activos`.
- [x] 2.3 Escribir tests de filtros: por `destinatario`, por `tamano`, por `ciudad` (modelo multi-ciudad coincide; modelo sin ciudades es general; ciudad no coincidente se oculta) y por combinación AND de los tres.
- [x] 2.4 Escribir tests de compatibilidad: un modelo solo con campos originales se muestra como activo, prioridad `media`, sin error.
- [x] 2.5 Escribir tests para `opciones_filtro_modelos()`: devuelve `{"destinatarios", "tamanos", "ciudades"}` ordenadas, sin duplicados, con `ciudades` aplanadas de todos los modelos.
- [x] 2.6 Implementar el mapa de rango de prioridad y el ordenamiento estable.
- [x] 2.7 Implementar `listar_modelos3d(destinatario=None, tamano=None, ciudad=None)` con filtros AND, ordenamiento y retorno `{"activos", "cubiertos"}`; ciudad coincide si `not ciudades` o `ciudad in ciudades`.
- [x] 2.8 Implementar `opciones_filtro_modelos()`; actualizar docstrings de la interfaz del repositorio.
- [x] 2.9 Ejecutar `uv run pytest` y confirmar que los tests nuevos pasan.

## 3. Ruta (`routes/paginas.py`)

- [x] 3.1 En `impresion_3d()`, leer `destinatario`, `tamano` y `ciudad` de `request.args` (vacío ⇒ `None`).
- [x] 3.2 Llamar a `contenido.listar_modelos3d(...)` y `contenido.opciones_filtro_modelos()` y pasar `modelos` (dict), `opciones` y los valores seleccionados a la plantilla.

## 4. Plantilla y estilos

- [x] 4.1 En `templates/impresion_3d.html`, añadir el `<form method="get">` con tres `<select>` (destinatario, tamaño, ciudad) preseleccionando el valor activo, siguiendo el markup de `puntos_acopio.html`.
- [x] 4.2 Renderizar los modelos activos con el indicador de prioridad (🔴/🟠/🟢) acompañado de texto/`aria-label` ("Prioridad alta/media/baja") para accesibilidad.
- [x] 4.3 Renderizar el grupo "Cubierto" solo cuando haya cubiertos, atenuado y tachado; mostrar mensaje de "sin resultados" cuando no haya activos ni cubiertos tras filtrar.
- [x] 4.4 Añadir la clase `.cubierto` (y, si hace falta, `.prioridad-*`) en `static/style.css`.

## 5. Verificación

- [x] 5.1 Ejecutar `uv run pytest` completo y confirmar que todo pasa.
- [x] 5.2 Levantar `uv run flask --app app run --debug` y verificar manualmente en `/impresion-3d`: orden por prioridad con iconos, filtros combinables (incluida ciudad multi-valor), grupo "Cubierto" atenuado y mensaje de "sin resultados".
- [x] 5.3 Ejecutar `openspec validate modelos-3d-prioridad-filtros` y corregir lo que reporte. (Con `--strict` solo aparecen avisos RFC-2119 por usar "DEBE" en vez de "SHALL/MUST"; se mantiene el español por consistencia con el repo.)
