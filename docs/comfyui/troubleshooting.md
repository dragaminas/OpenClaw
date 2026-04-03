# Troubleshooting de Workflows ComfyUI

Este documento implementa la tarea `8.16` del `DevPlan`.
Recoge problemas esperables del baseline y como distinguir entre una incidencia
real y una limitacion ya conocida del stack.

## Chequeo rapido

Antes de entrar en detalles:

```bash
scripts/apps/comfyui.sh status
scripts/apps/comfyui.sh manager-status
```

Si el servicio no esta levantado:

```bash
scripts/apps/comfyui.sh start-service
```

## VRAM insuficiente

Sintomas:

- el render cae a mitad de proceso
- `ComfyUI` deja de responder
- un clip corto funciona, pero uno largo no

Acciones:

- bajar a preset `preview`
- segmentar el plano
- reducir referencias simultaneas
- desactivar `depth` si no es imprescindible
- pasar de video completo a preprocess reutilizable

## Nodos faltantes

Sintomas:

- el workflow abre con nodos rojos
- `object_info` no expone el nodo esperado

Acciones:

- revisar `configs/comfyui/custom-nodes-manifest.md`
- confirmar que el nodo es backend y no solo decoracion frontend
- si falta `DepthAnything_V3`, usar la ruta `V2`
- si falta `ComfyUI-GGUF`, no prometer la ruta GGUF como activa
- si `ComfyUI` deja de arrancar tras instalar `ComfyUI-DepthAnythingV3`,
  revisar `prestartup_script.py`: el runtime local ya requiere tolerar la
  ausencia de `comfy_env` y `comfy_3d_viewers` en vez de abortar el arranque

## Modelos mal ubicados

Sintomas:

- `UNETLoader`, `CLIPLoader` o `VAELoader` no encuentran el archivo
- el workflow original usa subdirectorios que no existen en la maquina

Acciones:

- revisar `configs/comfyui/models-manifest.md`
- revisar `configs/comfyui/model-set-baseline-minimo-rtx3060-8gb-12gb.md`
- preferir las rutas ya normalizadas en `ComfyUIWorkflows/local/`

## Tiempos de render demasiado altos

Sintomas:

- el plano no cabe en una iteracion razonable
- la maquina se queda ocupada demasiado tiempo para validar look

Acciones:

- bajar resolucion
- cortar el shot en segmentos
- validar primero un keyframe o un tramo corto
- guardar el preprocess una sola vez y reutilizarlo

## Reanudacion de iteraciones

Regla practica:

- no repetir `preprocess` si los controles no cambiaron
- versionar los exports de Blender
- versionar tambien las salidas de `ComfyUI`

Esto permite volver a iterar sobre:

- prompt
- referencias
- LoRAs
- preset de calidad

sin reconstruir todo desde cero.

## No hay implementacion nativa todavia

Sintomas:

- el caso de uso existe en el catalogo, pero solo tiene variante `adaptable`
  o `future`

Que hacer:

- tratar el workflow como referencia, no como promesa de ejecucion inmediata
- usar el preset o template derivado mas cercano
- registrar el caso como pendiente de derivacion real

Ejemplos hoy:

- `UC-VID-03` depende todavia de template, no de una derivacion cerrada
- `UC-VID-04` tiene referencia de upscale, no flujo completo validado
- `UC-VID-02` sigue siendo biblioteca heredada aunque sus assets ya esten en
  disco

## Cuando parar y no insistir

Hay que dejar de insistir y registrar bloqueo cuando:

- falta un modelo grande no descargado
- el plugin requerido no esta instalado
- el fallback aun no esta habilitado
- el caso solo existe como referencia de `maximum`

En esos casos el sistema debe devolver un mensaje claro y dejar materiales o
documentacion utiles para continuar despues.
