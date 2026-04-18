# Troubleshooting de la Linea 3D

Este documento implementa la tarea `9.16` del `DevPlan`.
Recoge los problemas esperables al productizar `SF3D` como baseline del `MVP`.

## Nodos 3D ausentes

Sintomas:

- el workflow abre con nodos rojos
- no existen `StableFast3DLoader`, `StableFast3DSampler` o `StableFast3DSave`

Acciones:

- revisar `configs/comfyui/3d-custom-nodes-manifest.md`
- instalar primero `stable-fast-3d` oficial
- no vender el fallo como problema del prompt

## Modelo o acceso ausente

Sintomas:

- el loader de `SF3D` no descarga el modelo
- aparece error de acceso al repo gated
- no existe cache local del modelo

Acciones:

- revisar `configs/comfyui/3d-models-manifest.md`
- validar acceso a `Hugging Face`
- autenticar el `venv` o dejar el modelo cacheado localmente
- no confundir "workflow listo" con "modelo realmente accesible"

## Dependencias nativas rotas

Sintomas:

- `gpytoolbox` falla al importar
- `pynanoinstantmeshes` no existe
- `texture_baker` o `uv_unwrapper` no compilan

Acciones:

- alinear `numpy` a `1.26.x`
- instalar `pynanoinstantmeshes`
- compilar `texture_baker` y `uv_unwrapper`
- no intentar esconder este fallo detras de otro stack 3D mas pesado

## Runtime de `transformers` incompatible

Sintomas:

- aparece `cannot import name 'find_pruneable_heads_and_indices'`
- `SF3D` falla antes incluso de cargar la imagen

Acciones:

- alinear `transformers` con la baseline validada de `SF3D`
- en este entorno, la correccion operativa fue `transformers==4.42.3`
- si otras extensiones dependen de un `huggingface_hub` mas nuevo, aislar
  `SF3D` en un runtime o `venv` dedicado

## `texture_baker` sin kernel `CUDA`

Sintomas:

- aparece `Could not run 'texture_baker_cpp::rasterize' with arguments from the 'CUDA' backend`
- la malla se genera, pero el bake de texturas cae

Acciones:

- aceptar un fallback de bake en `CPU` para cerrar el `MVP`
- o recompilar `texture_baker` con `CUDA` real si se quiere recuperar ese
  tramo en GPU
- no confundir este problema con falta de acceso al modelo o con un fallo del
  workflow

## OOM o memoria insuficiente

Sintomas:

- la corrida cae al cargar el modelo o al arrancar el bake
- el sistema deja la GPU saturada

Acciones:

- reducir `texture_resolution`
- probar primero `remesh=none`
- pasar piezas grandes a un flujo por partes
- dejar el cleanup fino para `Blender`

## Zonas no visibles pobres

Sintomas:

- la parte trasera es incoherente
- el asset solo se sostiene desde el angulo original

Acciones:

- registrar el activo como proxy o suficiente, no como hero asset
- reforzar cleanup o cierre manual en `Blender`
- reservar una futura linea oficial `Hunyuan3D` fuera de `ComfyUI` si este
  criterio se vuelve dominante

## Ejes o escalas absurdas

Sintomas:

- el activo entra tumbado en `Blender`
- el activo entra gigante o diminuto

Acciones:

- aplicar el bridge `3D -> Blender`
- fijar `+Z up`, `-Y forward`, metros y pivot canonico
- volver a exportar el asset limpio desde `Blender`

## Escenas demasiado ambiciosas

Sintomas:

- una sola corrida no representa la escena completa
- la imagen mezcla demasiados objetos

Acciones:

- degradar a `blockout`
- pedir descomposicion por familias
- usar `UC-3D-02` varias veces en vez de forzar un solo mesh
