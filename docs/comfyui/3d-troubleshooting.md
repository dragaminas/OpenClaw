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
