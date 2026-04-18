# Decision `go/no-go` sobre `SF3D` como ruta principal del producto 3D

Este documento implementa la tarea `10.14` del `DevPlan`.
Cierra la decision formal sobre si `Stable Fast 3D` sigue siendo la ruta
principal o queda relegado a benchmark tecnico, evidencia historica o
contingencia secundaria.

## Decision

**`go` para relegar `SF3D` a benchmark tecnico y contingencia secundaria.**

A partir de la fase 10, `SF3D` no es la ruta principal del producto 3D.

## Fundamento

La decision se apoya en la evidencia acumulada de las fases 9 y 10:

### Lo que `SF3D` si entrega

- corridas tecnicamente exitosas en esta maquina (`RTX 3060 12 GB`)
- `glb` importable en `Blender` con vertices usables
- cierre tecnico de `AT-3D-OBJ-01`, `AT-3D-OBJ-02` y `CP-3D-01`
- demostracion de que la cadena `ComfyUI -> SF3D -> Blender` funciona

Esta evidencia queda en:
- `docs/comfyui/general-3d-object-workflow-results.md`
- `docs/comfyui/3d-atomic-composed-validation-results.md`

### Lo que `SF3D` no entrego

- calidad visual suficiente para sostenerlo como apuesta principal de producto
- caras dorsales convincentes desde una sola vista
- resultado inequivocamente superior a un proxy manual en `Blender`
- experiencia operativa limpia: los wrappers de `ComfyUI` para 3D añaden
  friccion de diagnostico y de mantenimiento sin justificacion suficiente

La fase 9 fue `pass tecnico` pero no `pass visual de producto`.

### Lo que `Hunyuan3D` promete completar en la fase 10

- calidad visual superior gracias a su arquitectura especifica para 3D
- un motor 3D separado con su propio `venv` y su propio puerto, mas limpio de
  depurar
- una `web UI` nativa como interfaz de operacion manual
- una `API` propia para futuros puntos de automatizacion
- las mismas taxonomia y contrato de I/O de la fase 9, reutilizados sin ruptura

## Estado del `go/no-go` para la fase 10 completa

| Criterio | Estado |
| --- | --- |
| Motor `Hunyuan3D-2mini-Turbo` instalado localmente | `pending_runtime` |
| Corrida real `UC-3D-02` con resultado importable en `Blender` | `pending_runtime` |
| Calidad visual superior a `SF3D` documentada | `pending_runtime` |
| Runner registrado y accesible desde CLI y WhatsApp | `done` |
| `SF3D` degradado a `LEGACY` en el catalogo | `done` |
| Contrato de I/O, troubleshooting y fallbacks actualizados | `done` |

**El `go` sobre el replanteo de arquitectura esta cerrado.**
**El `go` completo sobre calidad visual sigue pendiente del resultado de `10.10`.**

## Condicion de cierre final

La decision queda completamente cerrada cuando:

1. `docs/hunyuan3d/validation-results.md` registra `pass` en al menos
   `AT-H3D-OBJ-01` y `AT-H3D-OBJ-02`
2. la comparativa visual frente a `SF3D` esta documentada en ese mismo
   fichero
3. el resultado es claramente superior o al menos no inferior al de `SF3D`

Si al ejecutar la validacion real `Hunyuan3D-2mini-Turbo` no supera a `SF3D`
de forma clara, debe revisarse la decision antes de cerrar la fase 10, no
silenciarse el resultado.

## Que ocurre con `SF3D` a partir de aqui

| Uso | Estado |
| --- | --- |
| Ruta principal de producto 3D | `no` — retirado |
| Benchmark tecnico de referencia | `si` — conservado |
| Evidencia historica de fase 9 | `si` — conservada en `docs/comfyui/` |
| Fallback de ultimo recurso si `Hunyuan3D` no arranca | `permitido` con declaracion explicita |
| Comparativa visual en `validation-results.md` | `recomendada` para dar valor a la comparativa |

Los workflows `SF3D` en `ComfyUIWorkflows/local/` no se borran.
Su variante en el catalogo queda marcada con `maturity=LEGACY`.
El runner de `ComfyUI` sigue funcionando para imagen y video.

## Relacion con otros documentos

- evidencia fase 9: `docs/comfyui/3d-atomic-composed-validation-results.md`
- transicion de fase 9 a fase 10: `docs/hunyuan3d/phase-10-native-transition.md`
- perfiles de hardware: `docs/hunyuan3d/hardware-profiles.md`
- resultados de validacion fase 10: `docs/hunyuan3d/validation-results.md`
- fallbacks: `docs/hunyuan3d/fallback-paths.md`
