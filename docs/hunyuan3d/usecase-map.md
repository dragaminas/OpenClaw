# Mapa de Casos de Uso 3D sobre la Linea Nativa `Hunyuan3D`

Este documento implementa la tarea `10.4` del `DevPlan`.
Transpone los cuatro casos de uso `UC-3D-*` de la fase 9 a la nueva linea
nativa basada en `Hunyuan3D`, manteniendo los alias de producto y dejando
claro que cambia y que se conserva.

## Principio de transposicion

Los alias, el contrato de I/O y la taxonomia de fase 9 siguen vigentes.
Lo que cambia es el motor de inferencia 3D:

- antes: `ComfyUI + SF3D` como host de la generacion 3D
- ahora: `Hunyuan3D` nativo como aplicacion separada

La ruta `texto -> imagen` sigue sin ser nativa de `Hunyuan3D`.
Sigue requiriendo un puente a traves de `ComfyUI` o de una imagen de semilla
preparada manualmente.

## Mapa principal

| ID | Alias | Entrada | Entrega preferida | Motor fase 9 | Motor fase 10 |
| --- | --- | --- | --- | --- | --- |
| `UC-3D-01` | `texto-a-3d` | texto | `asset` aislado | `ComfyUI + SF3D` con imagen puente | `ComfyUI` genera semilla, `Hunyuan3D-2mini-Turbo` produce el `glb` |
| `UC-3D-02` | `imagen-a-3d` | imagen | `asset` aislado | `ComfyUI + SF3D` | `Hunyuan3D-2mini-Turbo` directo como baseline principal |
| `UC-3D-03` | `texto-a-escena-3d` | texto | `set`, `blockout` o `envolvente` | `ComfyUI + SF3D` por pieza | `ComfyUI` genera semillas por pieza, `Hunyuan3D` genera cada activo |
| `UC-3D-04` | `imagen-a-escena-3d` | imagen | `set`, `blockout` o `envolvente` | `ComfyUI + SF3D` por activo o crop | `Hunyuan3D` genera cada activo desde recorte o referencia aislada |

## Transposicion por caso

### `UC-3D-01` — `texto -> asset`

Ruta en fase 10:

```text
prompt
  -> ComfyUI genera imagen semilla
  -> imagen semilla entra a Hunyuan3D-2mini-Turbo
  -> shape-first output
  -> glb exportado
  -> Blender
```

Diferencias respecto a fase 9:

- el bloque `SF3D` de `ComfyUI` desaparece
- la imagen semilla sigue generandose en `ComfyUI` como antes
- `Hunyuan3D` reemplaza `SF3D` como motor 3D

Alias de catalogo conservado: `texto-a-3d`

### `UC-3D-02` — `imagen -> asset`

Ruta en fase 10:

```text
imagen de referencia (recortada, con alpha si es posible)
  -> Hunyuan3D-2mini-Turbo
  -> shape-first output
  -> glb exportado
  -> Blender
```

Este es el primer caso a validar en `10.10`.
Es la ruta mas directa y la unica que no necesita `ComfyUI` como paso previo.

Diferencias respecto a fase 9:

- `ComfyUI` es opcional, no obligatorio
- `Hunyuan3D Web UI` o `API` es la interfaz de inferencia

Alias de catalogo conservado: `imagen-a-3d`

### `UC-3D-03` — `texto -> set o blockout`

Ruta en fase 10:

```text
prompt
  -> ComfyUI genera imagen de concepto
  -> descomposicion de la escena en activos (manual o asistida)
  -> cada activo entra a Hunyuan3D-2mini-Turbo
  -> glb por pieza
  -> Blender compone
```

La salida valida sigue siendo `asset_set`, `envolvente` o `blockout`.
La escena monolitica sigue sin prometerse.

Alias de catalogo conservado: `texto-a-escena-3d`

### `UC-3D-04` — `imagen -> set o blockout`

Ruta en fase 10:

```text
imagen de referencia (interior, exterior, paisaje)
  -> recortar o aislar cada pieza principal
  -> cada recorte entra a Hunyuan3D-2mini-Turbo
  -> glb por pieza
  -> Blender ensambla
```

La referencia debe descomponerse antes de la inferencia.
No se trata de pasar la escena completa como input.

Alias de catalogo conservado: `imagen-a-escena-3d`

## Que se conserva sin cambios

- los cuatro alias de catalogo `UC-3D-0*`
- el contrato de entrada y salida documentado en `docs/hunyuan3d/io-contract.md`
- el puente a `Blender` y su normalizacion canonics
- la barra de calidad y los criterios de `pass/fail`
- la taxonomia de entrega: `asset`, `asset_set`, `blockout`, `envolvente`
- la regla de que `UC-3D-03` y `UC-3D-04` no prometen escena monolitica

## Que cambia de verdad

- el motor de inferencia 3D es ahora `Hunyuan3D` nativo, no `ComfyUI + SF3D`
- la app 3D corre en un proceso separado con su propio `venv` y su propio
  puerto
- `ComfyUI` queda solo como generador de semillas o preprocesos visuales para
  `UC-3D-01` y `UC-3D-03`
- la interfaz manual principal es la `web UI` de `Hunyuan3D` en lugar del
  grafo de `ComfyUI`

## Impacto sobre el catalogo Python

Los `FlowDefinition` existentes en `builtin_flow_catalog.py` usan hoy:

- `variant_id`: `sf3d-text-bridge-v1`, `sf3d-single-image-baseline`,
  `sf3d-scene-text-bridge`, `sf3d-scene-image-v1`

En esta fase, se añade una nueva variante nativa con `Hunyuan3D` por cada
caso de uso. Las variantes `SF3D` se degradan a `ImplementationMaturity.LEGACY`
o se conservan como benchmark secundario.

Nuevos `variant_id` propuestos:

| Caso | Nuevo `variant_id` |
| --- | --- |
| `UC-3D-01` | `hunyuan3d-2mini-turbo-text-bridge-v1` |
| `UC-3D-02` | `hunyuan3d-2mini-turbo-single-image-v1` |
| `UC-3D-03` | `hunyuan3d-2mini-turbo-scene-text-bridge-v1` |
| `UC-3D-04` | `hunyuan3d-2mini-turbo-scene-image-v1` |

## Relacion con otros documentos

- arquitectura de la linea nativa: `docs/hunyuan3d/native-runtime-architecture.md`
- perfiles de hardware y variantes: `docs/hunyuan3d/hardware-profiles.md`
- contrato de I/O: `docs/hunyuan3d/io-contract.md`
- interfaz operativa: `docs/hunyuan3d/interface.md`
- validaciones y evidencia: `docs/hunyuan3d/validation-results.md`
- composicion de escenas: `docs/hunyuan3d/scene-composition.md`
