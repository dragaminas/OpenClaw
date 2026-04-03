# Validacion E2E de Fase 8

Este documento implementa el entregable de `8.15`.
Registra el estado real de validacion de extremo a extremo de la Fase 8 en
`ComfyUI`, sin fingir que los casos bloqueados ya estan aprobados.

En esta fase la validacion no depende todavia de que Blender este listo.
La integracion `Blender -> ComfyUI` ya queda diseñada en otros entregables,
pero el cierre funcional de `8.15` puede apoyarse en material de prueba
cualquiera.

## Validaciones confirmadas

### Servicio y runtime

- `ComfyUI` local activo en `http://127.0.0.1:8188/`
- `object_info` responde
- los custom nodes principales para VHS, Wan, KJNodes, Impact y control
  preprocess estan cargados

### Biblioteca derivada

- existen workflows derivados en `ComfyUIWorkflows/local/`
- el catalogo Python apunta primero a variantes derivadas, no a originales
  crudos

## Matriz de validacion

| Caso | Estado | Motivo |
| --- | --- | --- |
| `UC-IMG-02` frame de prueba cualquiera | `ready_for_test` | el stack `Z-Image` y el patch local ya estan presentes; falta ejecutar la prueba real |
| `UC-VID-01` preprocess de controles | `ready_for_test` | `DepthAnything_V3` y el fallback `V2` ya estan disponibles; falta validar salidas sobre un clip |
| `UC-VID-02` video renderizado baseline | `reference_ready` | la biblioteca heredada puede quedar local, pero sigue siendo una ruta cuantizada y no la preferida para baseline |
| `UC-VID-03` imagen a video / first-last frame | `ready_for_test` | `Wan 2.2 5B fp16`, `umt5_xxl_fp16` y `wan2.2_vae` ya permiten preparar la prueba real |
| `UC-VID-04` mejora de video | `ready_for_test` | la ruta simple de upscale puede quedar lista; falta correrla sobre un clip concreto |

## Lectura correcta de 8.15

La tarea queda implementada como registro y criterio de validacion, pero la
aprobacion funcional completa sigue pendiente hasta correr pruebas reales con
material de entrada.

## Que valida primero el baseline

Orden recomendado con los modelos ya presentes:

1. `UC-IMG-02` con una imagen fija de prueba cualquiera
2. `UC-VID-01` sobre un clip corto cualquiera para comprobar el paquete de controles
3. `UC-VID-03` sobre un clip corto o sobre first/last frame derivados del material elegido
4. `UC-VID-02` solo como comparativa contra la biblioteca heredada

## Perfil recomendado del material de prueba

Para no bloquear la validacion por el propio clip:

- `3-5` segundos
- `24 fps`
- `480p` o `720p`
- movimiento legible pero no caotico
- fondo y sujeto relativamente claros

Puede ser:

- un video local ya existente
- un clip libre de prueba
- un export de Blender mas adelante, cuando esa capa ya este lista

## Evidencia local usada

- estado del servicio via `scripts/apps/comfyui.sh status`
- consulta de `http://127.0.0.1:8188/object_info`
- verificacion de modelos presentes en `/home/eric/ComfyUI/models`

## Criterio de cierre real

`8.15` solo deberia considerarse completamente cerrada cuando existan:

- una imagen fija de prueba entrando en `UC-IMG-02`
- un clip corto de prueba entrando en `UC-VID-01` y/o `UC-VID-02`
- artefactos de salida guardados con una convencion estable

La validacion especifica `Blender -> ComfyUI` puede quedar como aceptacion de
una fase posterior.
