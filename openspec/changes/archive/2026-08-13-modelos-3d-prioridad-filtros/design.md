## Context

Ver `proposal.md` (Why) para la motivación. Estado actual relevante:

- `services/contenido.py` es la **capa repositorio** (única que conoce el origen de datos). Hoy `listar_modelos3d()` devuelve la lista cruda de `data/contenido.yaml`. `/puntos-acopio` ya tiene el patrón completo a replicar: `listar_puntos(pais, ciudad)` filtra y `opciones_filtro()` deriva las opciones desde los datos; la ruta lee query params y la plantilla renderiza un `<form method="get">`.
- El sitio es solo lectura, sin base de datos: el mantenedor edita el YAML y hace push. Fase 2 reemplazará el repositorio por Postgres detrás de la misma interfaz, así que toda la lógica de orden/filtro debe vivir en `services/contenido.py`, no en la ruta ni en la plantilla.
- UI: Jinja2 + Pico CSS por CDN, con `static/style.css` para overrides.

## Goals / Non-Goals

**Goals:**
- Orden por prioridad + indicador visual, estado "cubierto" y filtros (destinatario/tamaño/ciudad) resueltos **dentro del repositorio**, dejando ruta y plantilla tan delgadas como las de `/puntos-acopio`.
- Campos nuevos 100% opcionales: el contenido existente sigue funcionando sin editar.
- Mantener la interfaz estable de cara a Fase 2 (Postgres).

**Non-Goals:**
- No hay formulario de envío ni panel de admin (eso es Fase 2). Marcar "cubierto" o la prioridad se hace editando el YAML.
- No se persiste el estado del filtro entre sesiones más allá de los query params en la URL (igual que `/puntos-acopio`).
- No se ordena por nada distinto a prioridad (sin orden por nombre/fecha).

## Decisions

### 1. Modelo de datos en YAML (campos opcionales por modelo)
Se añaden a cada entrada de `modelos_3d`:
- `prioridad`: `alta` | `media` | `baja`. Ausente ⇒ `media`.
- `destinatario`: p. ej. `personas` | `mascotas` (valor único).
- `tamano`: `pequeno` | `mediano` | `grande` (valor único; sin ñ para evitar problemas de tecleo/orden).
- `ciudades`: lista de strings. Ausente/vacía ⇒ alcance general (coincide con cualquier ciudad).
- `cubierto`: booleano. Ausente ⇒ `false` (activo).

*Por qué:* strings/booleanos simples son fáciles de curar a mano y triviales de mapear a columnas en Fase 2. `ciudades` como lista (no `ciudad` única) refleja la decisión del mantenedor: un mismo modelo puede necesitarse en varias ciudades, aunque el filtro sea de selección única. *Alternativa descartada:* enum estricto validado en carga — se prefiere tolerancia (valores desconocidos simplemente no matchean) para no romper el render por un typo en el YAML.

### 2. Ordenamiento estable por prioridad
Mapa de rango `{alta:0, media:1, baja:2}`; se ordena con `sorted(..., key=rango)`. `sorted` de Python es estable, por lo que el desempate conserva el orden del YAML sin lógica extra.

*Por qué:* cumple "orden por prioridad" + "desempate por orden de contenido" del spec con una sola llamada. Un valor de prioridad desconocido cae al rango de `media`.

### 3. Filtrado y separación de cubiertos en el repositorio
`listar_modelos3d(destinatario, tamano, ciudad)` aplica los filtros (AND), ordena por prioridad y separa activos de cubiertos. Para no cambiar el contrato de forma ambigua, devuelve un dict:

```
{
  "activos":   [ ...modelos activos ya ordenados... ],
  "cubiertos": [ ...modelos cubiertos ya ordenados... ],
}
```

Coincidencia de ciudad: `not ciudades` (lista vacía/ausente) ⇒ match; si tiene ciudades, match si `ciudad in ciudades`. Filtros vacíos ⇒ no restringen.

*Por qué el dict en vez de una sola lista:* la plantilla necesita dibujar dos grupos visualmente distintos ("activos" y "Cubierto"); devolverlos ya separados mantiene la plantilla sin lógica de negocio. *Alternativa considerada:* devolver una lista plana con un flag `cubierto` y que Jinja agrupe — se descarta porque empuja ordenamiento/agrupación a la plantilla, justo lo que Fase 2 quiere evitar. **Nota de compatibilidad:** cambiar el tipo de retorno de `listar_modelos3d()` obliga a actualizar su único consumidor (`routes/paginas.py`) y sus tests; no hay otros llamadores.

### 4. Opciones de filtro derivadas de los datos
Nueva función `opciones_filtro_modelos()` (espejo de `opciones_filtro()` para puntos) que devuelve `{"destinatarios": [...], "tamanos": [...], "ciudades": [...]}`, cada una como conjunto ordenado sin duplicados, aplanando `ciudades` de todos los modelos.

*Por qué separada de `opciones_filtro()`:* las opciones de puntos y de modelos provienen de colecciones distintas; mantenerlas en funciones separadas evita acoplarlas y respeta la interfaz por tipo de contenido.

### 5. Ruta y plantilla (mismo patrón que `/puntos-acopio`)
- `routes/paginas.py::impresion_3d()` lee `request.args` (`destinatario`, `tamano`, `ciudad`), llama al repositorio y pasa `modelos` (dict activos/cubiertos), `opciones` y los valores seleccionados a la plantilla.
- `templates/impresion_3d.html`: `<form method="get">` con tres `<select>` (mismo markup Pico que puntos), la lista de activos con el icono de prioridad, el grupo "Cubierto" (solo si hay cubiertos) atenuado/tachado, y el mensaje de "sin resultados".
- Icono de prioridad: emoji directo (🔴/🟠/🟢) vía un pequeño mapa en la plantilla o un helper; el tachado/atenuado del grupo cubierto se resuelve con una clase CSS en `static/style.css` (p. ej. `.cubierto { opacity:.6; text-decoration:line-through }`).

*Por qué emoji y CSS simple:* cero dependencias nuevas, accesible y coherente con el stack Pico + overrides existente.

## Risks / Trade-offs

- **Cambio de tipo de retorno de `listar_modelos3d()`** (lista ⇒ dict) → Mitigación: es un repo pequeño con un único consumidor; se actualiza ruta + tests en el mismo cambio. Se documenta la nueva forma en el docstring.
- **Valores libres en YAML (typos)** hacen que un modelo no matchee un filtro sin avisar → Mitigación: tolerancia por diseño (mejor no matchear que romper); los valores válidos se documentan como comentario en `data/contenido.yaml`.
- **`ciudades` como lista** puede confundir frente al `ciudad` singular de puntos de acopio → Mitigación: nombres distintos a propósito y comentario en el YAML; la semántica (multi-ciudad) queda fijada en el spec.
- **Emoji como único indicador de prioridad** podría no bastar para accesibilidad → Mitigación: acompañar el emoji con texto/`aria-label` (p. ej. "Prioridad alta"), no depender solo del color.

## Migration Plan

Cambio puramente aditivo en contenido y sin datos que migrar. Despliegue = merge + push (Railway redeploya). Rollback = revertir el commit; los campos nuevos son opcionales, así que revertir el código no rompe un YAML que ya los tenga (simplemente se ignoran). Sin variables de entorno nuevas.
