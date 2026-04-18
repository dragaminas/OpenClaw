# Transposicion de la Fase 9 a `Hunyuan3D` Nativo

Este documento abre la fase `10` del `DevPlan`.
Su funcion es trasladar la linea 3D del baseline `ComfyUI + SF3D` a una ruta
principal basada en `Hunyuan3D` nativo, sin reescribir la historia de la fase
9 ni mezclar ambos objetivos.

## Lectura correcta de la fase 9

La fase 9 deja valor real, pero su lectura debe afinarse:

- queda validada la taxonomia `UC-3D-*`
- queda validado el contrato base de entrada y salida
- queda validado el puente `3D -> Blender`
- queda validado que `ComfyUI` puede servir como benchmark tecnico de `SF3D`
- no queda validada una calidad visual suficiente para sostener `SF3D` como
  apuesta principal del producto 3D

En otras palabras:

- fase 9: `pass tecnico`
- lectura visual de producto: insuficiente

## Decision de replanteo

La linea 3D debe dejar de depender de `ComfyUI` como entorno principal de
inferencia 3D.

La apuesta recomendada pasa a ser:

- `ComfyUI` para imagen, video, seeds y preprocesados visuales
- `Hunyuan3D` nativo para generacion 3D
- `Blender` para inspeccion, cleanup, ensamblaje y handoff final

Documentos de apoyo ya abiertos para esta linea:

- `docs/hunyuan3d/hardware-profiles.md`
- `docs/hunyuan3d/native-runtime-architecture.md`

## Motivos del cambio

- evita que el runtime 3D quede condicionado por conflictos de `custom nodes`
  y dependencias compartidas con flujos de imagen o video
- separa mejor responsabilidades operativas y reduce confusion
- hace mas facil depurar fallos de calidad, rendimiento o compatibilidad
- permite usar `web UI` y `API` de `Hunyuan3D` como superficie propia, en vez
  de esconder el 3D dentro de wrappers de `ComfyUI`
- encaja mejor con la evidencia practica observada: `SF3D` ejecuta, exporta e
  importa, pero no esta cerrando la barra visual deseada

## Que se conserva de la fase 9

No se tira a la basura el trabajo previo.
La fase 10 debe reutilizar:

- `UC-3D-01` `texto -> objeto/personaje 3D`
- `UC-3D-02` `imagen -> objeto/personaje 3D`
- `UC-3D-03` `texto -> set de activos o escena`
- `UC-3D-04` `imagen -> set de activos o escena`
- la nomenclatura de outputs y artefactos
- el contrato de importacion a `Blender`
- la barra de calidad y los criterios de evidencia revisable
- el aprendizaje de que escenas complejas deben tratarse como composicion por
  piezas y no como mesh unico prometido demasiado pronto

## Que cambia de verdad

## Runtime

- deja de asumirse que el 3D corre dentro del mismo proceso Python de
  `ComfyUI`
- la linea 3D pasa a tener su propia aplicacion y su propio stack de
  dependencias

## Superficie operativa

- la operacion principal debe poder hacerse desde la `web UI` nativa de
  `Hunyuan3D`
- la automatizacion futura debe pasar por su `API` local y no por wrappers
  comunitarios de `ComfyUI`

## Lectura de producto

- la pregunta ya no es "que template 3D de `ComfyUI` usamos"
- la pregunta pasa a ser "que variante nativa de `Hunyuan3D` cierra mejor el
  baseline local y como la enchufamos al resto del sistema"

## Mapa de transposicion por caso de uso

| Caso | Lectura en fase 9 | Transposicion a fase 10 |
| --- | --- | --- |
| `UC-3D-01` | `texto -> imagen semilla -> SF3D` | mantener `texto -> imagen semilla`, pero pasar la generacion 3D a `Hunyuan3D` nativo |
| `UC-3D-02` | `imagen -> SF3D` | convertirlo en baseline principal `imagen -> Hunyuan3D` |
| `UC-3D-03` | imagen conceptual y `SF3D` por pieza | mantener el enfoque por piezas, pero generar cada activo con `Hunyuan3D` nativo |
| `UC-3D-04` | descomposicion de escena con `SF3D` por activo | conservar la descomposicion, sustituyendo el motor por la linea nativa |

## Regla de arquitectura

La fase 10 no debe crear dos productos 3D compitiendo entre si.

Regla recomendada:

- un solo baseline vigente de producto 3D
- una sola historia operativa para el operador
- `SF3D` queda como benchmark tecnico o fallback secundario
- `Hunyuan3D` nativo pasa a ser la ruta a defender si supera la barra visual

## Criterios de validacion para abrir la fase 10

Para considerar bien abierta esta fase, deben cumplirse estos minimos:

- la app nativa arranca de forma reproducible en la maquina local
- hay una corrida real de `UC-3D-02`
- el output entra en `Blender`
- la lectura visual queda documentada y comparada contra `SF3D`
- se deja claro si la ruta local cubre `shape-only`, texturizado o ambas cosas

## Criterio de cierre propuesto

La fase 10 solo deberia marcarse como `done` si:

- la linea nativa supera o corrige de forma clara la debilidad visual de la
  fase 9
- queda mas limpia de operar que la linea 3D previa en `ComfyUI`
- conserva la compatibilidad con `Blender` y con la taxonomia de casos del
  producto

## Cierre de la fase 10

Fecha de cierre de smoke: `2026-04-18`

### Lo que se resolvio

Tarea por tarea:

| Tarea | Entregable | Descripcion de la resolucion |
| --- | --- | --- |
| `10.1` | `phase-10-native-transition.md` | lectura oficial de fase 9: `pass tecnico / fail visual`; criterio de replanteo documentado |
| `10.2` | `hardware-profiles.md` | baseline elegido: `Hunyuan3D-2mini-Turbo` con `--low_vram_mode --enable_flashvdm`; perfiles remotos excluidos del alcance |
| `10.3` | `native-runtime-architecture.md` | arquitectura operativa: dos apps separadas, dos venvs, puertos `7860`/`8081`, carpetas `Assets3D/` |
| `10.4` | `usecase-map.md` | `UC-3D-01` a `UC-3D-04` transpuestos a la linea nativa; alias de producto conservados |
| `10.5` | `hardware-profiles.md` ampliado | tiempos objetivo y barra de calidad por perfil; comparativa frente a `SF3D` |
| `10.6` | `installation.md` + `install-hunyuan3d.sh` + `hunyuan3d.service.template` | instalacion reproducible ejecutada con exito: repo clonado, venv, pesos `25.3 GB`, PyTorch `2.11.0+cu130` |
| `10.7` | `io-contract.md` | contrato de I/O adaptado; carpeta `hunyuan3d/` bajo `Assets3D/`; formato de request JSON+base64 |
| `10.8` | `interface.md` | tres superficies: `web UI` port `7860`, `API` port `8081`, `WhatsApp`; mensajes de estado por evento |
| `10.9` | `smoke-validation.md` + `hunyuan3d-smoke-validation.sh` | bateria de `4` gates implementada; corrida real pasada con `PASS=10 FAIL=0` |
| `10.10` | `validation-results.md` | smoke: `AT-H3D-OBJ-01` y `AT-H3D-OBJ-02` en `pass`; `glb` `842 KB`, `23.376` vertices, inferencia `3.2 s` |
| `10.11` | `scene-composition.md` | `UC-3D-03` y `UC-3D-04` redefinidos como composicion por activos; no se promete escena monolitica |
| `10.12` | `troubleshooting.md` + `fallback-paths.md` | troubleshooting y degradacion documentados para la linea nativa |
| `10.13` | `hunyuan3d.py` + `registry.py` + `runner-integration.md` | `Hunyuan3DRunner` implementado y registrado; variantes `ADAPTABLE`; `SF3D` rebajado a `LEGACY` |
| `10.14` | `sf3d-decision.md` | decision formal: `SF3D` → benchmark/legacy; `Hunyuan3D` → ruta principal; condicion de cierre definida |

### Estado del smoke al cierre

Corrida de referencia:

```
bash scripts/apps/hunyuan3d-smoke-validation.sh
→ PASS=10  FAIL=0
→ glb: 842.348 bytes  vertices: 23.376  inferencia: 3.20 s
```

### Lo que queda pendiente de la fase

- `CP-H3D-01`: corrida `UC-3D-01` completa (`texto -> imagen -> Hunyuan3D`) con imagen creativa real
- comparativa visual frente a `SF3D` con la misma imagen del fixture de fase 9
- esa comparativa no es bloqueante del smoke; es el proximo paso natural
  antes de declarar victoria de producto
