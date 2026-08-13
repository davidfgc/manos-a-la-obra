## Why

Hoy la página `/impresion-3d` muestra todos los modelos en el orden en que aparecen en el YAML, sin señal de urgencia ni forma de acotar la lista. Durante una emergencia el voluntario necesita saber de un vistazo **qué imprimir primero** y filtrar por lo que puede aportar (para personas o mascotas, según el tamaño que su impresora soporte, y para su ciudad). Además, cuando una necesidad ya quedó cubierta, hoy no hay manera de comunicarlo y se sigue imprimiendo de más.

## What Changes

- La lista de modelos 3D se **ordena por prioridad** (alta → media → baja) y cada ítem muestra un **icono/indicador de prioridad** (🔴 alta, 🟠 media, 🟢 baja) para escanearla rápido.
- El mantenedor puede marcar un modelo como **ya no requerido / cubierto**; el ítem no desaparece: se muestra **atenuado y tachado** en un grupo aparte ("Cubierto") al final, para comunicar el progreso y evitar impresiones innecesarias.
- La lista se puede **filtrar** por:
  - **Destinatario**: personas / mascotas.
  - **Tamaño**: pequeño / mediano / grande.
  - **Ciudad**: un modelo puede necesitarse en **varias ciudades**; el filtro es de selección única y un modelo coincide si la ciudad elegida está entre las suyas. Un modelo sin ciudades declaradas se considera de alcance general y aparece con cualquier filtro de ciudad.
- Se amplían los campos curables de cada modelo en `data/contenido.yaml` (`prioridad`, `destinatario`, `tamano`, `ciudades`, `cubierto`) manteniendo compatibilidad con los modelos existentes (todos los campos nuevos son opcionales).
- La capa repositorio `services/contenido.py` amplía su interfaz para devolver los modelos ordenados y filtrados, y para exponer las opciones de filtro; las rutas y plantillas consumen esa interfaz igual que hoy hace `/puntos-acopio`.

## Capabilities

### New Capabilities
- `impresion-3d`: catálogo de modelos 3D imprimibles — priorización, indicador visual de prioridad, estado "cubierto/ya no requerido" y filtrado por destinatario, tamaño y ciudad.

### Modified Capabilities
<!-- Ninguna: no existen specs previas bajo openspec/specs/. -->

## Impact

- **Contenido**: `data/contenido.yaml` — nuevos campos opcionales por modelo (`prioridad`, `destinatario`, `tamano`, `ciudades`, `cubierto`).
- **Repositorio**: `services/contenido.py` — `listar_modelos3d()` gana ordenamiento + filtros + separación de cubiertos; nueva función de opciones de filtro para modelos (equivalente a `opciones_filtro()`).
- **Rutas**: `routes/paginas.py` — `impresion_3d()` lee query params de filtro y pasa opciones a la plantilla (mismo patrón que `puntos_acopio()`).
- **Plantilla**: `templates/impresion_3d.html` — formulario de filtros, orden por prioridad con icono, y grupo "Cubierto" atenuado.
- Sin dependencias nuevas. Sin variables de entorno. Compatible con la migración prevista a Postgres en Fase 2 (los cambios viven detrás de la interfaz del repositorio).
