# Automatizacion Minima de Export desde Blender

Este documento implementa la tarea `8.13` del `DevPlan`.
No crea aun un addon definitivo, pero define el minimo automatizable para que
Blender y `ComfyUI` se hablen sin friccion innecesaria.

## Objetivo

Reducir errores de nombre, carpeta y version al exportar pases de control.

## Alcance minimo

La automatizacion minima deberia hacer estas cinco cosas:

1. crear la estructura de carpetas del shot si no existe
2. exportar `lineart`, `depth`, `openpose` y `start frame` con nombres
   consistentes
3. guardar un manifiesto JSON del shot
4. no sobrescribir silenciosamente una version anterior
5. dejar un mensaje claro sobre que falta para ejecutar el flujo en `ComfyUI`

## Convenciones a automatizar

### Directorios

- `blender/frames/`
- `blender/controls/`
- `blender/refs/`
- `blender/manifests/`

### Artefactos

- `lineart`: video o secuencia
- `depth`: video o secuencia
- `openpose`: video o secuencia
- `start frame`: PNG
- `end frame`: PNG opcional

### Versionado

Regla sugerida:

- detectar ultimo `v###`
- generar siguiente version
- si el usuario fuerza una version, avisar antes de reusar nombre

## Salida minima que el bridge necesita

Si la automatizacion no puede exportar todo, el minimo aceptable es:

- `lineart`
- `start frame`
- `manifiesto`

Con eso ya puede correrse `UC-IMG-02` y dejar preparado parte de `UC-VID-01`.

## Lo que no hace falta automatizar todavia

- lanzar `ComfyUI` desde Blender
- disparar renders por API
- administrar prompts avanzados
- resolver todo el fallback desde Blender

## Propuesta de siguiente paso

La primera automatizacion real puede ser un script de Blender que:

- lea `project_id` y `shot_id`
- exporte a la estructura pactada
- escriba el manifiesto
- copie referencias elegidas a `refs/`

Con eso el lado `OpenClaw` ya puede ofrecer una interfaz guiada sin obligar a
la persona usuaria a pelear con rutas manuales.
