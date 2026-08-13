## Context

Ver `proposal.md` (Why). Estado actual relevante:

- `services/contenido.py` es la capa repositorio; ya expone `listar_modelos3d()`, `listar_puntos()`, `opciones_filtro*()`, todas leyendo `data/contenido.yaml` con el helper tolerante `_cargar()` (devuelve `{}` si falta o está malformado) y filtrando entradas que no son `dict`.
- `routes/paginas.py::index()` hoy hace `render_template("index.html")` sin pasar datos. El `x_handle` se inyecta globalmente vía context processor en `app.py`.
- `templates/index.html` termina con un `<article class="aside-x">` (bloque de contacto por X). La nueva sección va **después** de ese bloque.
- El sistema de diseño ya define `article`, `.btn`, tipografía y tokens en `static/style.css`.

## Goals / Non-Goals

**Goals:**
- Grupos como contenido curado editable en el YAML, servido por el repositorio, sin lógica en plantilla/ruta más allá de renderizar.
- Sección extensible (hoy 1 grupo, mañana N) sin tocar código.
- Tolerancia a datos malformados, como el resto del repositorio.

**Non-Goals:**
- No hay filtros, orden especial ni categorías de grupos (se listan en el orden del YAML).
- No se validan las URLs ni se comprueba que el grupo exista/esté activo.
- No es una página propia: es una sección dentro de la home.

## Decisions

### 1. Nueva clave `grupos` en el YAML
Lista de objetos `{nombre, url}`:
```yaml
grupos:
  - nombre: "Makers unidos por Colombia"
    url: "https://chat.whatsapp.com/FxATszkflYa8xzBwwN65kj?s=cl&p=i&ilr=4"
```
*Por qué:* mismo patrón de datos que `modelos_3d`/`puntos_acopio`; trivial de curar y de mapear a una tabla en Fase 2.

### 2. `listar_grupos()` en el repositorio
```python
def listar_grupos(*, path=DATA_PATH):
    grupos = _cargar(path).get("grupos") or []
    return [g for g in grupos if isinstance(g, dict) and g.get("nombre") and g.get("url")]
```
Filtra entradas no-dict y las que carezcan de `nombre` o `url`. Devuelve lista (posiblemente vacía). Misma forma e idioma que `listar_modelos3d()` original.

*Por qué:* la tolerancia (ignorar malformados) evita romper la home por un error de tipeo en el YAML, consistente con `listar_puntos`/`opciones_filtro`.

### 3. Ruta y plantilla
- `index()` pasa `grupos=contenido.listar_grupos()` a `index.html`.
- `index.html`: tras `<article class="aside-x">`, un bloque condicional `{% if grupos %}` con encabezado "Otros grupos" y una lista de enlaces (`target="_blank" rel="noopener"`). Sin grupos, no se renderiza nada.

*Por qué inyectar por la ruta y no por context processor:* los grupos solo se usan en la home; pasarlos por la ruta evita cargar el YAML en cada vista (los otros templates no los necesitan).

## Risks / Trade-offs

- **Enlaces externos a grupos de mensajería** pueden caducar (invitaciones de WhatsApp) → Mitigación: es contenido curado; el mantenedor actualiza el YAML. Fuera del alcance validar disponibilidad.
- **Sin orden explícito** → se listan en el orden del YAML; si más adelante se quiere orden alfabético o por tipo, es un cambio menor posterior. Se documenta como Non-Goal.

## Migration Plan

Cambio puramente aditivo: clave `grupos` opcional en el YAML, función nueva en el repositorio, sección condicional en la home. Sin datos que migrar, sin variables de entorno. Rollback = revertir el commit; un YAML que ya tenga `grupos` simplemente se ignora si el código se revierte.
