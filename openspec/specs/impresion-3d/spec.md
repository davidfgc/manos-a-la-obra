# impresion-3d Specification

## Purpose

Define el comportamiento observable de la página de modelos 3D imprimibles: cómo se priorizan los modelos, cómo se comunica que una necesidad ya fue cubierta, y cómo el voluntario acota la lista por destinatario, tamaño y ciudad.

## Requirements

### Requirement: Orden por prioridad con indicador visual

La página de modelos 3D DEBE mostrar los modelos activos ordenados por prioridad de mayor a menor (`alta`, luego `media`, luego `baja`) y, dentro de la misma prioridad, DEBE conservar el orden en que aparecen en el contenido curado. Cada modelo DEBE mostrar un indicador visual de su prioridad (icono/color): 🔴 para `alta`, 🟠 para `media`, 🟢 para `baja`. Un modelo sin prioridad declarada DEBE tratarse como prioridad `media`.

#### Scenario: Ordenamiento de mayor a menor prioridad
- **WHEN** el contenido tiene modelos con prioridades `baja`, `alta` y `media`
- **THEN** la lista los muestra en el orden `alta`, `media`, `baja`

#### Scenario: Desempate por orden de contenido
- **WHEN** dos modelos activos tienen prioridad `alta`
- **THEN** se muestran en el mismo orden relativo en que aparecen en el contenido curado

#### Scenario: Indicador visible por ítem
- **WHEN** se renderiza un modelo de prioridad `alta`
- **THEN** el ítem incluye el indicador visual correspondiente a prioridad alta (🔴)

#### Scenario: Prioridad ausente se asume media
- **WHEN** un modelo no declara prioridad
- **THEN** se ordena y se muestra como prioridad `media`

### Requirement: Estado "ya no requerido / cubierto"

El contenido curado DEBE permitir marcar un modelo como ya no requerido (cubierto). Un modelo cubierto NO DEBE eliminarse de la página: DEBE mostrarse atenuado y tachado dentro de un grupo separado ("Cubierto / ya no se necesita") ubicado después de todos los modelos activos. Los modelos no marcados DEBEN mostrarse como activos en la lista priorizada.

#### Scenario: Modelo cubierto se separa y atenúa
- **WHEN** un modelo está marcado como cubierto
- **THEN** aparece en el grupo "Cubierto", atenuado y tachado, después de los modelos activos

#### Scenario: Modelo activo permanece en la lista priorizada
- **WHEN** un modelo no está marcado como cubierto
- **THEN** aparece entre los modelos activos ordenados por prioridad, no en el grupo "Cubierto"

#### Scenario: Sin modelos cubiertos no se muestra el grupo
- **WHEN** ningún modelo está marcado como cubierto
- **THEN** la página no muestra el grupo "Cubierto"

### Requirement: Filtro por destinatario

La página DEBE permitir filtrar los modelos por destinatario con selección única entre las opciones disponibles (por ejemplo `personas`, `mascotas`). Cuando se elige un destinatario, la página DEBE mostrar únicamente los modelos cuyo destinatario coincide. Sin destinatario seleccionado, DEBEN mostrarse todos. Las opciones ofrecidas DEBEN derivarse de los destinatarios presentes en el contenido.

#### Scenario: Filtrar por destinatario
- **WHEN** el voluntario selecciona el destinatario `mascotas`
- **THEN** solo se muestran modelos cuyo destinatario es `mascotas`

#### Scenario: Sin selección muestra todos los destinatarios
- **WHEN** no se selecciona ningún destinatario
- **THEN** se muestran modelos de todos los destinatarios

#### Scenario: Opciones derivadas del contenido
- **WHEN** el contenido solo contiene modelos con destinatario `personas`
- **THEN** el filtro de destinatario no ofrece la opción `mascotas`

### Requirement: Filtro por tamaño

La página DEBE permitir filtrar los modelos por tamaño con selección única entre las opciones disponibles (por ejemplo `pequeno`, `mediano`, `grande`). Cuando se elige un tamaño, DEBE mostrar únicamente los modelos de ese tamaño. Sin tamaño seleccionado, DEBEN mostrarse todos. Las opciones ofrecidas DEBEN derivarse de los tamaños presentes en el contenido.

#### Scenario: Filtrar por tamaño
- **WHEN** el voluntario selecciona el tamaño `pequeno`
- **THEN** solo se muestran modelos de tamaño `pequeno`

#### Scenario: Sin selección muestra todos los tamaños
- **WHEN** no se selecciona ningún tamaño
- **THEN** se muestran modelos de todos los tamaños

### Requirement: Filtro por ciudad con modelos multi-ciudad

Un modelo DEBE poder asociarse a varias ciudades donde se necesita. El filtro de ciudad DEBE ser de selección única y, al elegir una ciudad, la página DEBE mostrar los modelos cuya lista de ciudades incluye la ciudad elegida. Un modelo sin ciudades declaradas DEBE considerarse de alcance general y DEBE aparecer con cualquier ciudad seleccionada. Las opciones de ciudad DEBEN derivarse de las ciudades presentes en el contenido, sin duplicados y ordenadas.

#### Scenario: Modelo con varias ciudades coincide con una elegida
- **WHEN** un modelo declara las ciudades `Bogotá` y `Cali`, y el voluntario filtra por `Cali`
- **THEN** el modelo se muestra

#### Scenario: Modelo sin ciudades es de alcance general
- **WHEN** un modelo no declara ninguna ciudad y el voluntario filtra por `Bogotá`
- **THEN** el modelo se muestra

#### Scenario: Ciudad no coincidente se oculta
- **WHEN** un modelo declara solo la ciudad `Medellín` y el voluntario filtra por `Bogotá`
- **THEN** el modelo no se muestra

#### Scenario: Opciones de ciudad sin duplicados
- **WHEN** varios modelos declaran la ciudad `Bogotá`
- **THEN** el filtro de ciudad ofrece `Bogotá` una sola vez

### Requirement: Combinación de filtros

Los filtros de destinatario, tamaño y ciudad DEBEN poder combinarse; un modelo DEBE mostrarse solo si cumple todas las condiciones seleccionadas. El ordenamiento por prioridad y la separación de modelos cubiertos DEBEN preservarse sobre el resultado filtrado. Si ninguna coincidencia queda tras aplicar los filtros, la página DEBE mostrar un mensaje de "sin resultados".

#### Scenario: Filtros combinados aplican todas las condiciones
- **WHEN** el voluntario filtra por destinatario `personas`, tamaño `pequeno` y ciudad `Bogotá`
- **THEN** solo se muestran modelos que son para `personas`, de tamaño `pequeno` y disponibles en `Bogotá`

#### Scenario: Orden y agrupación se preservan tras filtrar
- **WHEN** el resultado filtrado contiene modelos activos y cubiertos de distintas prioridades
- **THEN** los activos se muestran ordenados por prioridad y los cubiertos, atenuados, en su grupo al final

#### Scenario: Sin coincidencias muestra mensaje
- **WHEN** ningún modelo cumple la combinación de filtros seleccionada
- **THEN** la página muestra un mensaje indicando que no hay modelos para ese filtro

### Requirement: Compatibilidad con contenido existente

Todos los campos nuevos de un modelo (`prioridad`, `destinatario`, `tamano`, `ciudades`, `cubierto`) DEBEN ser opcionales. Un modelo que solo declara los campos previos (`nombre`, `descripcion`, `url`, `material`, `categoria`) DEBE seguir mostrándose sin error, tratado como activo y con prioridad `media`.

#### Scenario: Modelo heredado se muestra sin campos nuevos
- **WHEN** un modelo solo tiene los campos originales y ninguno de los nuevos
- **THEN** se muestra como activo, con prioridad `media`, y sin provocar error
