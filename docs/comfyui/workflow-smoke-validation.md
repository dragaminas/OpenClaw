# Smoke Validation Minima para Desbloquear 8.18

Este documento implementa la tarea `8.19` del `DevPlan`.
Define una validacion ligera previa a `8.18` para comprobar que los workflows
derivados realmente corren en local sin pedir todavia calidad alta ni una
revision E2E exigente.

## Objetivo

Desbloquear `8.18` con una puerta de entrada mas barata:

- comprobar que cada workflow carga
- comprobar que acepta inputs minimos
- comprobar que llega a ejecutar
- comprobar que guarda al menos una salida util
- evitar que `8.18` falle por intentar empezar con pruebas demasiado pesadas

## Runner operativo

La smoke suite ya se puede correr con:

```bash
scripts/apps/comfyui-smoke-validation.sh --run-id smoke-light-5
```

La evidencia queda en:

- `~/Studio/Validation/comfyui/smoke/<run-id>/manifests/summary.json`
- `~/Studio/Validation/comfyui/smoke/<run-id>/evidence/summary.md`

El contrato general que deberia gobernar esta ejecucion vive en:

- `docs/architecture/runner-interface.md`

## Extension correcta hacia WhatsApp

El siguiente paso no deberia crear una estructura paralela solo porque la UI
actual sea WhatsApp.

La idea correcta para `8.20` es extender la misma estructura que ya existe en
`8.19`:

- mismo runner local
- mismos `case_id`
- mismos manifiestos y rutas de evidencia
- mismo criterio de estados (`pass`, `soft_pass_with_fallback`, `fail_runtime`)
- mismo modelo de publicacion de artefactos

WhatsApp deberia actuar como capa de entrada y seguimiento sobre esa base, no
como una segunda implementacion distinta para lanzar tests o usar `ComfyUI`.

La especificacion concreta de esa extension vive en:

- `docs/comfyui/whatsapp-comfyui-extension.md`

## Lectura correcta

`8.19` no sustituye a `8.18`.

La idea es:

1. `8.19` valida que el workflow funciona a nivel smoke
2. `8.18` valida despues la corrida atomica y compuesta con evidencia mas seria

Si un workflow no pasa `8.19`, no tiene sentido pedirle todavia la validacion
mas completa de `8.18`.

## Principios

- el objetivo es confirmar funcionamiento, no calidad final
- la prueba debe ser lo bastante pequena como para repetirse facil
- no hace falta medir fidelidad visual fina
- no hace falta comparar contra una referencia `maximum`
- no hace falta optimizar duraciones ni calidad de render
- una salida fea pero valida puede contar como `pass` en smoke
- una prueba no cuenta si hubo que abrir el grafo y corregir nodos a mano

## Perfil de fixtures para smoke

Para abaratar tiempo, VRAM y riesgo, las pruebas smoke deberian usar:

- imagen fija:
  - `512 x 512` o `640 x 384`
  - `1` sujeto principal
  - fondo simple
  - PNG o JPG ligero
- clip de video:
  - `2-3` segundos
  - `12-16 fps`
  - `320p` o `480p`
  - una sola accion o desplazamiento simple
  - sin audio obligatorio
- referencias:
  - `1` referencia de personaje cuando el flujo la necesite
  - `1` referencia de estilo opcional como maximo

## Suite smoke minima

| Test | Caso | Input minimo | Pasa si |
| --- | --- | --- | --- |
| `SMK-IMG-02-01` | `UC-IMG-02` | `1` imagen pequena + `1` prompt corto | el workflow carga, ejecuta y deja `1` still guardado |
| `SMK-VID-01-01` | `UC-VID-01` | `1` clip pequeno | el workflow exporta al menos `outline` y `pose`; `depth` puede salir por `V3` o fallback `V2` |
| `SMK-VID-02-01` | `UC-VID-02` | `1` clip pequeno o paquete de controles pequeno + `1` prompt corto | deja `1` render corto guardado sin edicion manual |
| `SMK-IMG-03-01` | `UC-IMG-03` | `1` still pequeno + refs opcionales | deja al menos `1` variante guardada |
| `SMK-VID-03-01` | `UC-VID-03` | `1` frame inicial + `1` frame final + prompt opcional | genera `1` clip corto reconocible |
| `SMK-VID-04-01` | `UC-VID-04` | `1` clip pequeno ya renderizado | genera `1` clip mejorado guardado |

## Criterio de pase

Una smoke test cuenta como `pass` cuando:

- el workflow abre sin nodos rotos
- los modelos minimos requeridos estan presentes o existe fallback declarado
- la corrida entra en cola y termina
- queda al menos un artefacto en la ruta esperada
- el artefacto no esta vacio ni corrupto a simple vista
- no hubo que editar el JSON ni recolocar nodos durante la prueba

Para `UC-VID-02` en la `RTX 3060`, tambien se acepta `soft_pass_with_fallback`
cuando el workflow:

- compila sin nodos rotos
- entra realmente en la ruta pesada de `Wan/VACE`
- sigue corriendo mas de `90s`
- se interrumpe a proposito para que `8.19` siga siendo un gate barato

Ese caso no sustituye la validacion seria de `8.18`; solo certifica que el
workflow ya esta cableado y arranca de verdad.

## Criterio de no pase

La smoke test debe marcarse como:

- `fail_runtime` si la ejecucion rompe antes de guardar salida
- `blocked_missing_asset` si faltan modelos, nodos o inputs
- `soft_pass_with_fallback` si corre usando un fallback ya aceptado
- `soft_pass_with_fallback` si un workflow pesado como `UC-VID-02` entra en su
  ruta real de render pero se corta al pasar el umbral de smoke
- `fail_quality` solo si la salida es claramente inutil o esta rota, no por ser
  simplemente fea

## Orden recomendado

Orden minimo para desbloquear `8.18` con el menor riesgo posible:

1. `SMK-IMG-02-01`
2. `SMK-VID-01-01`
3. `SMK-VID-02-01`
4. `SMK-VID-04-01`
5. `SMK-IMG-03-01`
6. `SMK-VID-03-01`

## Que deberia quedar listo al cerrar 8.19

`8.19` solo deberia cerrarse cuando existan:

- fixtures pequenos y estables para imagen y video
- una manera repetible de lanzar cada smoke test
- rutas de salida simples y estables
- evidencia minima de que cada workflow al menos corre
- un criterio claro para decidir si ya merece entrar en `8.18`

## Relacion con 8.18

`8.18` pasa a ser ejecutable de forma realista cuando `8.19` ya redujo el
riesgo inicial.

La secuencia correcta seria:

1. correr smoke validation de `8.19`
2. corregir nodos, assets o presets rotos
3. correr la validacion atomica y compuesta de `8.18`
4. registrar resultados en
   `docs/comfyui/atomic-composed-whatsapp-validation-results.md`
