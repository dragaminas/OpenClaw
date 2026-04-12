# Interfaz Objetivo para la Linea 3D

Este documento implementa la tarea `9.7` del `DevPlan`.
Define como deberia conversar la UI con la persona usuaria cuando el objetivo
es producir `assets`, `sets` o `blockouts` 3D.

## Decision principal

La interfaz principal debe seguir siendo una sesion guiada.

La primera pregunta no deberia ser el prompt.
La primera pregunta deberia ser el tipo de entrega:

- `asset`
- `set de activos`
- `envolvente`
- `blockout`

Despues se resuelve:

- `texto` o `imagen`
- `objeto`, `personaje` o `envolvente`
- si la referencia ya viene recortada o con alpha
- si se trata de una pieza, un shell o un `blockout`

## Secuencia minima guiada

1. que quieres recibir: `asset`, `set`, `envolvente` o `blockout`
2. quieres partir de `texto` o de `imagen`
3. que categoria predomina: `objeto`, `personaje`, `envolvente`
4. tienes una imagen ya recortada o hace falta aislar mejor la pieza
5. quieres una pieza aislada o varias piezas para componer despues
6. que tamano aproximado o escala buscas

## Modo experto

El modo experto puede exponer directamente:

- `workflow`
- `preset`
- `hardware_profile`
- `seed`
- `steps`
- `guidance`

Pero no deberia sustituir la ruta guiada.

## Mensajes de usuario

Mensajes recomendados:

- inicio: "Voy a preparar una ruta 3D pensada para Blender y activos reutilizables."
- puente desde texto: "Primero necesito una imagen semilla; despues la pasare por Stable Fast 3D."
- escena compleja: "Esta referencia conviene descomponerla en piezas antes que forzar una escena monolitica."
- bloqueo por stack: "Todavia falta dejar operativa la extension oficial de SF3D o el acceso al modelo gated."

## Presets operativos a exponer

La capa guiada debe reutilizar estos presets:

- `uc-3d-01-text-to-asset-sf3d-bridge`
- `uc-3d-02-image-to-asset-sf3d-single-image`
- `uc-3d-03-text-to-scene-sf3d-asset-pack-bridge`
- `uc-3d-04-image-to-scene-sf3d-asset-pack`

## Regla de producto

La interfaz debe empujar la decision correcta de producto:

- primero piezas reutilizables
- despues composicion fina en `Blender`

No deberia empujar por defecto:

- escena final monolitica
- textura pesada
- camino `24 GB+` disfrazado de baseline
