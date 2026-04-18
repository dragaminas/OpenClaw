# Perfiles de Hardware para `Hunyuan3D` Nativo

Este documento implementa la tarea `10.2` del `DevPlan`.
Fija la variante nativa recomendada de `Hunyuan3D` para cada perfil de
hardware, con especial foco en la maquina local `RTX 3060 12 GB`.

## Corte temporal y fuentes

Fecha de corte de esta decision: `2026-04-18`.

Fuentes oficiales usadas para esta seleccion:

- repo oficial `Hunyuan3D-2`:
  `https://github.com/Tencent-Hunyuan/Hunyuan3D-2`
- repo oficial `Hunyuan3D-2.1`:
  `https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1`

Ademas se toma como evidencia interna el historico local ya derivado en:

- `ComfyUIWorkflows/local/historical/hunyuan-3d-validacion-de-hipotesis/minimum/uc-3d-02-image-to-asset-hunyuan-v2mini-turbo-shapegen-rtx3060-v1.json`
- `ComfyUIWorkflows/local/historical/hunyuan-3d-validacion-de-hipotesis/minimum/uc-3d-02-image-to-asset-hunyuan21-shapegen-rtx3060-v1.json`

## Decision principal

La variante nativa objetivo para la maquina local `RTX 3060 12 GB` debe ser:

- `Hunyuan3D-2mini-Turbo`
- modo `shape-first`
- `low_vram_mode`
- texturizado no baseline, pero si permitido como prueba explicita

La linea recomendada no es `Hunyuan3D-2.1` completo.
Tampoco debe venderse `shape + texture` como baseline local de `12 GB`.

## Motivo de la decision

Segun el repo oficial de `Hunyuan3D-2`:

- la familia `2.0` soporta `Gradio App`, `API Server` y `Blender Addon`
- el coste declarado es `6 GB VRAM` para `shape generation`
- y `16 GB` para `shape + texture`

Segun el repo oficial de `Hunyuan3D-2.1`:

- el coste declarado es `10 GB` para `shape`
- `21 GB` para `texture`
- y `29 GB` para `shape + texture` en total

Lectura operativa:

- `2.1` shape-only podria entrar de forma ajustada en `12 GB`, pero deja muy
  poco margen para convivir con otros procesos y no es la ruta mas limpia para
  un baseline local
- `2.1` con texturizado queda fuera del baseline local
- en `2.0`, el dato oficial de `16 GB` para `shape + texture` obliga a leer el
  texturizado en `3060 12 GB` como prueba oportunista y no como promesa estable
- `2mini-Turbo` encaja mejor con la promesa de una app local separada,
  iterativa y repetible

## Regla de seleccion por familia

### `Hunyuan3D-2mini-Turbo`

Debe ser la apuesta principal cuando importe:

- cerrar `UC-3D-02` local de forma estable
- iterar rapido sobre una sola imagen
- trabajar con `RTX 3060 12 GB`
- dejar el texturizado fuera del baseline, pero disponible para pruebas
  puntuales cuando el caso lo justifique

### `Hunyuan3D-2mini`

Debe mantenerse como comparativa local cuando importe:

- probar si la variante no `Turbo` recupera algo de calidad
- aceptar mas latencia a cambio de una segunda referencia local

No deberia ser la primera ruta operativa del baseline.

### `Hunyuan3D-2mv` y `2mv-Turbo`

Solo tienen sentido si de verdad disponemos de:

- varias vistas coherentes
- un contrato multivista real
- o una escena/pieza donde la multivista compense la complejidad extra

No deben ser baseline para entradas de una sola imagen.

### `Hunyuan3D-2.0` completo

Puede ser una linea de referencia o un perfil mejorado cuando haya:

- mas VRAM local o remota
- interes real en probar `shape + texture`
- margen para depender de un flujo mas pesado

No debe prometerse como baseline de `12 GB`.

### `Hunyuan3D-2.1`

Debe tratarse como linea de calidad alta o futura:

- `shape-only` cabe como benchmark exigente
- `texture` y `shape + texture` exigen perfiles superiores
- no es la apuesta correcta para una `3060 12 GB` como ruta principal

## Perfiles canonicos

| Perfil | Hardware de referencia | Variante recomendada | Objetivo realista |
| --- | --- | --- | --- |
| `minimum` | `RTX 3060 12 GB` local | `Hunyuan3D-2mini-Turbo` | `shape-first` usable desde una imagen y textura como prueba explicita |
| `adaptable` | `16 GB-20 GB VRAM` local o remota ligera | `Hunyuan3D-2mini` o `Hunyuan3D-2.0` shape-first | mas margen para iteracion y pruebas de textura selectiva |
| `high_vram` | `24 GB+` local o remota | `Hunyuan3D-2.0` con textura, `2.1` shape-only | calidad y texturizado con menos friccion |
| `pbr_remote` | `29 GB+` remota | `Hunyuan3D-2.1` completo | `shape + PBR texture` como ruta alta |

## Recomendacion concreta para esta maquina

La recomendacion operativa para la `RTX 3060 12 GB` es esta:

1. baseline local:
   `Hunyuan3D-2mini-Turbo`
2. modo de trabajo:
   `image -> shape -> Blender`
3. texturizado:
   fuera de baseline, pero dentro del alcance de prueba en esta misma maquina
4. comparativa secundaria:
   `Hunyuan3D-2mini` no `Turbo`
5. benchmark aspiracional:
   `Hunyuan3D-2.1` solo `shape-only`, no como baseline

## Mapa por caso de uso

| Caso | Ruta recomendada en `minimum` | Nota |
| --- | --- | --- |
| `UC-3D-01` | `texto -> imagen semilla -> Hunyuan3D-2mini-Turbo` | el puente desde texto sigue fuera del motor 3D |
| `UC-3D-02` | `imagen -> Hunyuan3D-2mini-Turbo` | debe ser el primer caso a validar |
| `UC-3D-03` | imagen semilla o conceptual y piezas por separado | no prometer escena monolitica |
| `UC-3D-04` | descomponer referencia y generar activos por pieza | `asset_set`, `blockout` o envolvente antes que escena final |

## Regla de producto

Para el baseline local, la promesa correcta no es:

- `PBR`
- texturas hero
- escena cerrada
- maximo detalle en caras no visibles

La promesa correcta si puede ser:

- mesh util
- lectura volumetrica mejor que `SF3D`
- handoff limpio a `Blender`
- una aplicacion 3D separada y menos ambigua de operar

Y, como prueba no baseline:

- validar si ciertos activos aceptan texturizado suficiente tambien en `3060`

## Comandos de referencia

Interfaz `Gradio` recomendada para baseline local:

```bash
python3 gradio_app.py \
  --model_path tencent/Hunyuan3D-2mini \
  --subfolder hunyuan3d-dit-v2-mini-turbo \
  --texgen_model_path tencent/Hunyuan3D-2 \
  --low_vram_mode \
  --enable_flashvdm
```

Comparativa local mas conservadora:

```bash
python3 gradio_app.py \
  --model_path tencent/Hunyuan3D-2mini \
  --subfolder hunyuan3d-dit-v2-mini \
  --texgen_model_path tencent/Hunyuan3D-2 \
  --low_vram_mode
```

Prueba explicita de texturizado en la misma linea:

- mantener `2mini-Turbo` como shape model
- activar textura solo en corridas de validacion concretas
- registrar siempre tiempo, uso de memoria y calidad visual observada

## Regla de descarte

No deberia abrirse la fase `10.10` con ninguna de estas rutas como baseline:

- `Hunyuan3D-2.1` completo en `3060 12 GB`
- `Hunyuan3D-2.0` con textura activada como promesa normal local
- variantes multivista si el input real sigue siendo una sola imagen

Si se prueba textura en `3060`, debe leerse como:

- experimento de validacion
- no garantia de throughput
- no compromiso de producto por defecto

## Tiempos objetivo por perfil

Los tiempos siguientes son orientativos para `shape-first` sin textura.
No son benchmarks cerrados sino rangos esperados validados contra la
arquitectura de cada perfil.

| Perfil | Variante | Modo | Tiempo orientativo | Nota |
| --- | --- | --- | --- | --- |
| `minimum` | `Hunyuan3D-2mini-Turbo` | `shape-first`, `low_vram` | `60-120 s` | Turbo reduce pasos de inferencia; no debe ser menos de `60 s` |
| `minimum` | `Hunyuan3D-2mini` | `shape-first`, `low_vram` | `2-5 min` | Mas pasos que Turbo; mas calidad, pero mas espera |
| `minimum` | textura añadida | `2mini-Turbo + texture` | `+8-15 min` | Alto uso de VRAM; puede fallar o caer con otros procesos activos |
| `adaptable` | `Hunyuan3D-2mini` o `2.0` | `shape-first` | `1-3 min` | Mas margen para textura selectiva |
| `high_vram` | `Hunyuan3D-2.0` | `shape + texture` | `5-15 min` | Rutaseria con textura activada por defecto |
| `pbr_remote` | `Hunyuan3D-2.1` | `shape + PBR texture` | `>15 min` | Alta calidad pero fuera de baseline local |

Regla operativa para el perfil `minimum`:

- si una iteracion de `shape-first` tarda mas de `10 min` en `2mini-Turbo`,
  sospechar de un problema de configuracion, no aceptarlo como normal
- si el proceso cae por OOM antes de terminar, revisar si otros programas
  pesados estan activos en la misma session
- el tiempo de descarga inicial del modelo no cuenta como tiempo de inferencia;
  se hace una sola vez y queda cacheado localmente

## Barra de calidad por perfil

### Perfil `minimum` — `Hunyuan3D-2mini-Turbo`

Requisitos minimos para considerar el resultado util:

- malla cerrada o reparable con cleanup ligero en `Blender`
- volumen legible al girar 360 grados en el visor
- orientacion corregible sin ambiguedad: un eje claro de `up`, una cara
  legible como frente
- escala corregible con un factor de escalado razonable
- pivot usable para composicion
- `glb` importable en `Blender` sin error fatal
- mejora visual clara frente a `SF3D` al menos en los casos donde `SF3D`
  quedaba pobre: zonas dorsales, silueta general

No se exige en el baseline `minimum`:

- textura final
- UV perfectas
- topologia de produccion
- rig o armature
- `PBR` completo

### Perfil `adaptable`

Igual que `minimum`, pero ademas:

- la textura puede activarse en prueba selectiva
- la iteracion puede ser mas lenta sin que sea un fallo

### Perfil `high_vram` y `pbr_remote`

- textura en el baseline si el caso lo justifica
- calidad de malla y UV por encima del perfil `minimum`

## Comparativa de referencia frente a `SF3D`

Para considerar la transposicion a `Hunyuan3D` justificada, debe observarse:

- que la silueta general del activo sea visiblemente mas correcta que `SF3D`
  en el mismo input
- que las zonas dorsales no visibles sean notoriamente mejores o al menos no
  peores
- que el handoff a `Blender` sea tan limpio o mejor

Si `Hunyuan3D-2mini-Turbo` no supera esta comparativa de forma clara, debe
anotarse en `docs/hunyuan3d/validation-results.md` y revisarse antes de
marcar la fase 10 como cerrada.

