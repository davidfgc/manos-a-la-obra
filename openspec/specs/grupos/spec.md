# grupos Specification

## Purpose

Define cómo la página de inicio presenta un directorio curado de grupos y comunidades externas de ayuda (por ejemplo grupos de WhatsApp de makers o voluntarios) para que quien llega pueda sumarse.

## Requirements

### Requirement: Sección de grupos en la página de inicio

La página de inicio DEBE mostrar una sección titulada "Otros grupos" ubicada **después** del bloque de contacto por X. La sección DEBE listar los grupos curados disponibles. Cada grupo DEBE presentarse con su nombre como enlace que abre en una pestaña nueva de forma segura (`target="_blank"` y `rel="noopener"`).

#### Scenario: Se muestra el grupo disponible después del contacto de X
- **WHEN** existe un grupo curado "Makers unidos por Colombia" con su URL
- **THEN** la home muestra la sección "Otros grupos", después del bloque de contacto por X, con "Makers unidos por Colombia" como enlace a esa URL

#### Scenario: El enlace abre de forma segura en pestaña nueva
- **WHEN** se renderiza un grupo
- **THEN** su enlace usa `target="_blank"` y `rel="noopener"`

### Requirement: Grupos como contenido curado

Los grupos DEBEN provenir del contenido curado (una lista de entradas con `nombre` y `url`), servidos por la capa repositorio con la misma interfaz de solo lectura que el resto del contenido. Agregar o quitar grupos DEBE hacerse editando el contenido, sin modificar plantillas ni rutas. Las entradas malformadas (que no sean objetos, o sin `nombre` o sin `url`) DEBEN ignorarse sin romper la página.

#### Scenario: Nuevo grupo agregado al contenido aparece en la home
- **WHEN** el mantenedor agrega un segundo grupo al contenido curado
- **THEN** la home lo muestra junto al existente, sin cambios en plantillas ni rutas

#### Scenario: Entrada malformada se ignora
- **WHEN** el contenido de grupos incluye una entrada sin `url` o que no es un objeto
- **THEN** esa entrada se omite y las válidas se siguen mostrando sin error

### Requirement: Sección oculta sin grupos

Cuando no hay grupos válidos cargados, la página de inicio NO DEBE mostrar la sección "Otros grupos" (sin encabezado ni estado vacío).

#### Scenario: Sin grupos no se muestra la sección
- **WHEN** el contenido no declara grupos válidos
- **THEN** la home no muestra la sección "Otros grupos"
