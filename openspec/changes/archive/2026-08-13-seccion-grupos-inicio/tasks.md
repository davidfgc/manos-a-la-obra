## 1. Contenido

- [x] 1.1 En `data/contenido.yaml`, agregar la clave `grupos` con el primer grupo: `{nombre: "Makers unidos por Colombia", url: "https://chat.whatsapp.com/FxATszkflYa8xzBwwN65kj?s=cl&p=i&ilr=4"}`.

## 2. Repositorio (`services/contenido.py`) — TDD

- [x] 2.1 Escribir tests para `listar_grupos()`: devuelve los grupos válidos; ignora entradas no-dict y las que carezcan de `nombre` o `url`; devuelve `[]` cuando no hay clave `grupos` o el archivo falta.
- [x] 2.2 Implementar `listar_grupos(*, path=DATA_PATH)` filtrando entradas inválidas.

## 3. Ruta y plantilla

- [x] 3.1 En `routes/paginas.py::index()`, pasar `grupos=contenido.listar_grupos()` a la plantilla.
- [x] 3.2 En `templates/index.html`, tras `<article class="aside-x">`, agregar la sección condicional `{% if grupos %}` "Otros grupos" con la lista de enlaces (`target="_blank"`, `rel="noopener"`).

## 4. Verificación

- [x] 4.1 Escribir/actualizar un test de página: la home muestra "Otros grupos" y "Makers unidos por Colombia" cuando hay grupos.
- [x] 4.2 Ejecutar `uv run pytest` y confirmar que todo pasa.
- [x] 4.3 Ejecutar `openspec validate seccion-grupos-inicio` y corregir lo que reporte.
