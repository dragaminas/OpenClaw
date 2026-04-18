# Rutas Fallback para la Linea Nativa `Hunyuan3D`

Este documento forma parte de la tarea `10.12` del `DevPlan`.
Define como degradar la entrega cuando la linea nativa no llega al objetivo
original, y actualiza los mensajes de producto para que reflejen que el
motor 3D ya no vive en `ComfyUI`.

## Principio

El fallback correcto no es "abandonar el 3D".
Es conservar valor util con una entrega mas modesta y ser honesto sobre ello.

## Orden de degradacion para `UC-3D-02` (imagen a asset)

1. intentar `shape-first` con `Hunyuan3D-2mini-Turbo`
2. si hay OOM: cerrar `ComfyUI` si corre, reintentar con `--low_vram_mode`
3. si sigue fallando: intentar `octree_resolution` menor
4. si el motor no esta instalado: retornar `blocked_missing_runtime`
5. si la malla sale sin valor: degradar a proxy (`blockout` manual en Blender)
6. si la GPU no disponible: reservar para perfil superior o ejecucion remota

## Orden de degradacion para `UC-3D-01` (texto a asset)

1. `ComfyUI` genera imagen semilla
2. imagen semilla entra a `Hunyuan3D-2mini-Turbo`
3. si `Hunyuan3D` no esta listo: devolver imagen semilla y dejar pendiente
   la etapa 3D hasta que el motor este operativo
4. si la semilla no tiene suficiente calidad: mejorar prompt y regenerar
5. misma degradacion que `UC-3D-02` a partir del paso 2

## Orden de degradacion para `UC-3D-03` y `UC-3D-04` (escena y set)

1. descomponer en piezas individuales y lanzar `UC-3D-02` por pieza
2. si una pieza no genera bien: degradarla a proxy y continuar con las otras
3. si la escena de origen es demasiado compleja: reducir a las dos piezas mas
   importantes primero
4. si el hardware no llega: devolver `envolvente` o `blockout` manual
5. si el motor no esta instalado: devolver lista de activos objetivo y descripcion
   de composicion sin geometria por ahora

## Fallbacks que no deben venderse como equivalentes

- una imagen bonita si el usuario pidio un asset rotatorio
- un solo activo si el usuario pidio un set
- una malla OOM falsa que pretende ser un blockout
- `SF3D` activado de nuevo como ruta principal (es benchmark, no producto)

## Estado de la linea `SF3D` en el contexto de estos fallbacks

`SF3D` puede usarse como:

- comparativa tecnica
- evidencia historica de la fase 9
- fallback de ultimo recurso si `Hunyuan3D` no esta disponible en ningun
  perfil

`SF3D` no debe usarse como:

- ruta principal del producto 3D
- equivalente silencioso cuando `Hunyuan3D` falla

Si el sistema usa `SF3D` como fallback en una corrida real, debe indicarlo
explicitamente en el manifest y en la respuesta al operador.

## Mensajes de producto para cada fallback

| Fallback activado | Mensaje al operador |
| --- | --- |
| `shape-first` sin textura | "Generando solo la forma 3D. La textura no esta disponible en este perfil." |
| motor no instalado | "El motor 3D nativo no esta listo todavia. Ejecuta install-hunyuan3d.sh primero." |
| OOM | "La GPU no tiene margen ahora. Cierra ComfyUI y reintenta." |
| malla degradada a proxy | "Esta pieza no genero bien. La incluyo como bloque base para Blender." |
| escena reducida a asset_set | "Esta escena tiene demasiados elementos. Estoy generando las piezas mas importantes por separado." |
| solo imagen semilla disponible | "He preparado la imagen semilla. La etapa 3D queda pendiente de instalacion del motor." |
| fallback a SF3D | "Ho podido usar Hunyuan3D. Usando SF3D como alternativa. El resultado es de referencia, no de producto." |
