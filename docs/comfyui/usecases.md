# Casos de Uso de ComfyUI

Este documento es la fuente de verdad para la tarea `8.1` del `DevPlan`.
Su objetivo es describir las capacidades que queremos ofrecer con `ComfyUI`
desde una perspectiva funcional, evitando atarlas demasiado pronto a un
workflow, a un JSON concreto o a una combinacion fija de nodos.

## Objetivo

Definir interfaces funcionales claras para imagen y video, junto con sus
variantes de implementacion posibles, para que el proyecto pueda evolucionar
sin tener que reescribir la capa de producto cada vez que cambie un workflow
base.

Este documento no define la UI final ni la automatizacion definitiva. Eso se
resolvera despues en las tareas `8.2`, `8.12`, `8.13` y `8.14`.

## Principios de modelado

- Una interfaz funcional describe que quiere lograr la persona usuaria.
- Una variante de implementacion describe como resolvemos esa interfaz con el
  stack disponible en un momento dado.
- Un escenario operativo combina una o varias interfaces funcionales para
  resolver una necesidad real de produccion.
- La capa conversacional y la futura UI deben exponer capacidades, no nombres de
  workflows ni detalles internos de ComfyUI.
- La seleccion de variante debe depender de entradas disponibles, hardware,
  coste, longitud del plano y nivel de control requerido.
- La captura de parametros deberia ser iterativa y guiada.
- El sistema no deberia exigir un prompt complejo desde el inicio salvo en modo
  experto.

## Principio de interaccion

La forma primaria de uso deberia ser una sesion interactiva guiada. La persona
usuaria expresa primero una intencion simple y el sistema se encarga de pedir,
en orden, solo los datos que falten para ejecutar la interfaz funcional
correcta.

Ejemplos de intencion inicial:

- `quiero crear una imagen`
- `quiero renderizar este video`
- `quiero convertir estas dos imagenes en un video`
- `quiero mejorar este video`

Esto implica:

- no tratar el prompt complejo como requisito de entrada inicial
- dividir la captura en pasos breves y comprensibles
- inferir parametros cuando sea razonable
- proponer defaults seguros para hardware local
- presentar un resumen final antes de ejecutar
- permitir modo experto para quien quiera introducir mas datos de golpe

## Capas del sistema

## 1. Interfaz funcional

Contrato estable de producto. Ejemplos:

- `texto -> imagen`
- `imagen base -> frame renderizado`
- `video base + referencias -> video renderizado`

## 2. Variante de implementacion

Forma concreta de ejecutar una interfaz funcional. Ejemplos:

- workflow local con `Z-Image Turbo CN`
- pipeline local `Preprocess -> AI Renderer 2.0`
- variante cloud en `Runpod`
- variante local con fallback `GGUF`

## 3. Perfil de ejecucion

Condiciones del entorno que restringen la ejecucion:

- `local-rtx3060-12gb`
- `runpod-high-vram`

## 4. Escenario operativo

Combinacion de interfaces funcionales para resolver un trabajo real. Ejemplos:

- crear un still de look-dev desde Blender
- convertir una rough animation en un plano corto renderizado
- mantener continuidad de estilo entre varios planos

## Estado de partida

- Hardware local previsto: `RTX 3060 12 GB`, `62 GiB RAM`, `Ryzen 5 5600X`.
- Workflows ya presentes en el repo:
  - `ComfyUIWorkflows/260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json`
  - `ComfyUIWorkflows/260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json`
  - `ComfyUIWorkflows/260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json`
  - `ComfyUIWorkflows/260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json`
- Direccion general del pipeline:
  `Blender -> materiales de entrada -> ComfyUI -> imagen o video final`.

## Escala de prioridad

- `P0`: desbloquea el pipeline base y deberia funcionar en local con ajustes
  conservadores.
- `P1`: muy valioso, pero depende de haber validado al menos un caso `P0`.
- `P2`: util o deseable, pero no bloquea la primera version operativa.

## Catalogo de interfaces funcionales

Estas interfaces son la capa estable que queremos ofrecer. Sus implementaciones
pueden cambiar con el tiempo.

| ID | Prioridad | Interfaz funcional | Resultado buscado | Estado inicial |
| --- | --- | --- | --- | --- |
| `UC-IMG-01` | `P0` | `texto -> imagen` | Generar una imagen guiada por prompt y referencias opcionales | adaptable ahora |
| `UC-IMG-02` | `P0` | `imagen base -> frame renderizado` | Transformar una imagen base en un frame final con control visual | disponible ahora |
| `UC-VID-01` | `P0` | `video base -> paquete de controles` | Extraer materiales de control reutilizables para video | disponible ahora |
| `UC-VID-02` | `P0` | `video base + referencias -> video renderizado` | Renderizar un plano a partir de una base animada y material de referencia | disponible ahora |
| `UC-VID-03` | `P1` | `imagen inicial + imagen final -> video` | Generar una transicion o plano guiado por keyframes extremos | adaptable ahora |
| `UC-VID-04` | `P1` | `video renderizado -> video mejorado` | Upscale, remaster o mejora de salida ya generada | futura variante |
| `UC-IMG-03` | `P2` | `imagen o frame -> variantes de estilo` | Explorar estilos, LoRAs y acabados reutilizables | adaptable ahora |

## Parametros canonicos transversales

Estos parametros no pertenecen a un workflow concreto. Son el contrato que la
interfaz deberia exponer, aunque cada variante use solo un subconjunto.

- `prompt`: descripcion textual del resultado buscado
- `referencias_personaje`: imagenes para identidad visual de personajes
- `referencias_estilo`: imagenes para tono, materialidad o look
- `loras_opcionales`: LoRAs de personaje, estilo o acabado
- `entrada_base`: imagen, secuencia o video sobre el que se apoya el render
- `controles_visuales`: contorno, profundidad, pose u otros controles que se
  puedan activar
- `perfil_ejecucion`: local o cloud
- `tamanio_objetivo`: resolucion o clase de calidad deseada
- `duracion_objetivo`: longitud del clip o numero de frames
- `modo_segmentacion`: ejecucion completa o fragmentada en bloques
- `semilla_o_variacion`: cuando interese reproducibilidad o exploracion

## Modelo de captura guiada

La captura guiada se puede pensar como una sesion con `slots` o campos que se
van completando progresivamente.

## Slots principales

- `intencion`: que interfaz funcional quiere activar la persona usuaria
- `material_entrada`: imagen, video, secuencia o ausencia de entrada base
- `objetivo_visual`: que resultado quiere conseguir
- `referencias`: personajes, estilo u otras imagenes de apoyo
- `controles`: que tipos de control visual quiere activar
- `perfil`: local o cloud segun coste, tiempo y hardware
- `alcance`: imagen unica, lote corto, plano breve o secuencia

## Reglas de captura

- pedir primero lo imprescindible para identificar la interfaz funcional
- pedir despues solo los parametros que esa interfaz realmente necesita
- no pedir controles avanzados si no cambian la decision de variante
- si falta algo no esencial, proponer un default en vez de bloquear la sesion
- resumir siempre lo entendido antes de ejecutar

## Estados de una sesion

1. `deteccion de intencion`
2. `completado de slots obligatorios`
3. `captura opcional de refinamientos`
4. `resumen y confirmacion`
5. `ejecucion`
6. `resultado y siguientes pasos`

## Seleccion de variantes

La interfaz funcional no deberia pedir a la persona usuaria que elija un JSON
especifico. La eleccion de variante deberia hacerse a partir de reglas como
estas:

- si hay una sola imagen de entrada y buscamos un frame final, priorizar
  `UC-IMG-02`
- si no hay imagen base y solo hay descripcion textual, usar `UC-IMG-01`
- si el trabajo es de video y faltan controles, ejecutar antes `UC-VID-01`
- si el plano es corto y el hardware local alcanza, priorizar variante local
- si el plano es largo o pesado, evaluar variante cloud o ejecucion segmentada
- si la VRAM local no alcanza, evaluar fallback `GGUF` o bajar perfil de salida

## Interfaces funcionales en detalle

## `UC-IMG-01` `texto -> imagen`

- Problema:
  necesitamos generar una imagen a partir de una descripcion textual, con
  soporte opcional para referencias y LoRAs, sin exigir una imagen base.
- Entradas minimas:
  - `prompt`
- Entradas opcionales:
  - `referencias_personaje`
  - `referencias_estilo`
  - `loras_opcionales`
  - `tamanio_objetivo`
- Salidas esperadas:
  - una o varias imagenes finales
  - metadatos suficientes para reproducir o iterar
- Variantes de implementacion:
  - `V1` futura variante local de `texto -> imagen`
  - `V2` variante cloud para mas calidad o batch
  - `V3` variante derivada que use una imagen vacia o base sintetica si hace
    falta acoplarla a un workflow existente
- Captura guiada recomendada:
  - pedir primero que quiere generar
  - luego pedir descripcion breve
  - despues ofrecer referencias y estilos como refinamientos opcionales
- Notas:
  - hoy no es la capacidad mejor cubierta por los workflows presentes, pero es
    una interfaz de producto valida y conviene modelarla ya.

## `UC-IMG-02` `imagen base -> frame renderizado`

- Problema:
  queremos convertir una imagen base en un frame final mas rico, preservando
  composicion o estructura y aplicando controles visuales opcionales.
- Entradas minimas:
  - `prompt`
  - `entrada_base`
- Entradas opcionales:
  - `referencias_personaje`
  - `referencias_estilo`
  - `loras_opcionales`
  - `controles_visuales`
- Salidas esperadas:
  - uno o varios frames finales comparables
- Variantes de implementacion:
  - `V1` local actual: `Z-Image Turbo CN 1.1`
  - `V2` local futura: otra variante `img2img` con diferente balance entre
    control y estilo
  - `V3` cloud: batch de calidad superior o mayor resolucion
- Captura guiada recomendada:
  - pedir imagen base
  - pedir una descripcion simple del resultado
  - ofrecer referencias, LoRAs y controles como pasos opcionales
- Casos tipicos:
  - still de look-dev desde Blender
  - keyframe estilizado
  - frame controlado con contorno, profundidad o pose

## `UC-VID-01` `video base -> paquete de controles`

- Problema:
  antes de renderizar video final, necesitamos producir materiales intermedios
  reutilizables a partir de una base animada.
- Entradas minimas:
  - `entrada_base` como video o secuencia de frames
- Entradas opcionales:
  - `controles_visuales` deseados
  - `tamanio_objetivo`
- Salidas esperadas:
  - secuencia normalizada
  - pases de contorno
  - pases de profundidad
  - pases de pose
  - convencion de nombres y carpetas consistente
- Variantes de implementacion:
  - `V1` local actual: `AI RENDERER - PREPROCESS 1.0`
  - `V2` futura: export automatizado desde Blender sin paso manual intermedio
- Captura guiada recomendada:
  - pedir video o secuencia de entrada
  - preguntar que controles quiere extraer
  - si no lo sabe, proponer `todos` como default
- Casos tipicos:
  - rough animation
  - animatica
  - viewport render

## `UC-VID-02` `video base + referencias -> video renderizado`

- Problema:
  necesitamos transformar una base animada en un plano renderizado con estilo,
  continuidad y control visual.
- Entradas minimas:
  - `prompt`
  - `entrada_base` o paquete de controles
- Entradas opcionales:
  - `referencias_personaje`
  - `referencias_estilo`
  - `loras_opcionales`
  - `controles_visuales`
  - `modo_segmentacion`
  - `duracion_objetivo`
- Salidas esperadas:
  - clip renderizado
  - si hace falta, varios fragmentos compatibles para recomposicion
- Variantes de implementacion:
  - `V1` local actual: `AI RENDERER 2.0`
  - `V2` cloud actual/adaptable: `AI RENDERER 2.0 Runpod`
  - `V3` local futura: fallback `GGUF` o perfil de memoria reducida
- Captura guiada recomendada:
  - pedir video base o paquete de controles
  - pedir descripcion breve del plano
  - pedir referencias visuales si existen
  - proponer segmentacion automatica si el plano excede el perfil local
- Notas:
  - en `RTX 3060 12 GB` hay que asumir resoluciones y longitudes conservadoras
  - la segmentacion deberia ser parte normal de esta interfaz, no una excepcion

## `UC-VID-03` `imagen inicial + imagen final -> video`

- Problema:
  queremos generar una transicion o un plano guiado por dos keyframes extremos,
  sin exigir necesariamente una animacion base completa.
- Entradas minimas:
  - `prompt`
  - `imagen_inicial`
  - `imagen_final`
- Entradas opcionales:
  - `referencias_personaje`
  - `referencias_estilo`
  - `loras_opcionales`
  - `duracion_objetivo`
- Salidas esperadas:
  - clip corto con continuidad entre inicio y final
- Variantes de implementacion:
  - `V1` adaptable con nodos tipo `start-to-end-frame`
  - `V2` futura variante dedicada de `keyframe-to-video`
- Captura guiada recomendada:
  - pedir imagen inicial
  - pedir imagen final
  - pedir duracion o dejar que el sistema proponga una
- Casos tipicos:
  - transicion entre ilustraciones
  - plano breve entre poses o composiciones ya aprobadas

## `UC-VID-04` `video renderizado -> video mejorado`

- Problema:
  despues de generar un video base, puede hacer falta mejorar resolucion,
  limpieza o acabado final.
- Entradas minimas:
  - `video_renderizado`
- Entradas opcionales:
  - `tamanio_objetivo`
  - `perfil_ejecucion`
  - `modo_segmentacion`
- Salidas esperadas:
  - video mejorado o reescalado
- Variantes de implementacion:
  - `V1` futura variante local de upscale
  - `V2` futura variante cloud para remaster pesado
- Captura guiada recomendada:
  - pedir video de entrada
  - preguntar si la prioridad es resolucion, limpieza o acabado
  - dejar que el sistema elija variante segun coste y hardware
- Estado:
  - esta interfaz es relevante para producto, aunque aun no tenga workflow base
    preparado en el repo

## `UC-IMG-03` `imagen o frame -> variantes de estilo`

- Problema:
  necesitamos explorar acabados y LoRAs sin mezclar ese trabajo con los flujos
  de produccion final.
- Entradas minimas:
  - `entrada_base`
  - `prompt`
- Entradas opcionales:
  - `referencias_estilo`
  - `loras_opcionales`
- Salidas esperadas:
  - conjunto de variantes comparables
  - base para elegir estilo reutilizable por proyecto
- Variantes de implementacion:
  - `V1` local actual: derivado de `UC-IMG-02`
  - `V2` local o cloud: exploracion en lote para biblia visual
- Captura guiada recomendada:
  - pedir imagen base
  - pedir que quiere explorar: personaje, estilo o acabado
  - proponer lote corto de variantes por defecto

## Escenarios operativos priorizados

Estos no son la interfaz en si, sino necesidades reales que se resuelven
componiendo una o varias interfaces funcionales.

| ID | Prioridad | Escenario | Interfaces implicadas |
| --- | --- | --- | --- |
| `SCN-01` | `P0` | Still de look-dev desde Blender | `UC-IMG-02` |
| `SCN-02` | `P0` | Preprocess de rough animation o animatica | `UC-VID-01` |
| `SCN-03` | `P0` | Plano corto de prueba desde Blender | `UC-VID-01` + `UC-VID-02` |
| `SCN-04` | `P1` | Biblia visual por secuencia | `UC-IMG-01` + `UC-IMG-02` + `UC-IMG-03` |
| `SCN-05` | `P1` | Plano corto final con referencias multiples | `UC-VID-01` + `UC-VID-02` |
| `SCN-06` | `P1` | Secuencia larga o pesada en cloud | `UC-VID-01` + `UC-VID-02` |
| `SCN-07` | `P2` | Continuidad de estilo entre varios planos | `UC-VID-02` + `UC-IMG-03` |
| `SCN-08` | `P2` | Remaster o upscale de salida final | `UC-VID-04` |

## Interfaz conversacional preliminar

La conversacion con el sistema deberia estar basada en intencion e inputs, no
en nombres internos de workflow.

Ejemplos deseables:

- `quiero crear una imagen desde texto`
- `quiero crear una imagen a partir de una imagen base`
- `quiero renderizar un video a partir de una animacion base`
- `quiero convertir una imagen inicial y una final en un video`
- `quiero mejorar este video`

El sistema deberia despues abrir un flujo de recoleccion de parametros, por
ejemplo:

1. identificar la interfaz funcional
2. pedir solo los parametros que falten
3. elegir la variante de implementacion adecuada
4. ejecutar con el perfil de hardware compatible
5. devolver salida y metadatos de reuso

## Sesion guiada frente a prompt complejo

Decision de producto propuesta:

- modo principal: sesion guiada por pasos
- modo secundario: entrada compacta o experta para usuarios avanzados

Motivos:

- reduce carga cognitiva
- facilita uso por personas no tecnicas
- mejora la calidad de los datos recogidos
- permite adaptar la ejecucion al hardware local sin exponer complejidad
- hace mas facil reutilizar la misma interfaz con variantes distintas

## Implicaciones para el compositor de workflows

- El compositor deberia vivir en scripts de Python u otra capa equivalente,
  pero su entrada deberia ser una interfaz funcional y un contrato de
  parametros, no un workflow fijo.
- Los workflows base se deberian tratar como plantillas adaptables.
- La activacion de controles como contorno, profundidad o pose deberia
  expresarse como opcion funcional, no como nodos expuestos a la persona usuaria.
- Para video, la segmentacion y reanudacion deberian considerarse capacidades
  nativas del sistema cuando el hardware local lo requiera.
- La salida deberia incluir suficiente metadata para reintentar, variar o mover
  la ejecucion a otro perfil.

## Orden recomendado de implementacion

1. `UC-IMG-02`
2. `UC-VID-01`
3. `UC-VID-02`
4. `UC-IMG-01`
5. `UC-IMG-03`
6. `UC-VID-03`
7. `UC-VID-04`

## Casos fuera del alcance inmediato

- exponer toda la complejidad interna de ComfyUI en la interfaz de usuario
- obligar a elegir workflows manualmente para operaciones comunes
- descarga automatica ciega de nodos y modelos sin manifiesto
- generar video largo de alta resolucion completamente en local sin
  segmentacion
- acoplar la logica de producto a un unico workflow de Mickmumpitz

## Como extender este documento

- Mantener IDs estables con el formato `UC-*` para interfaces y `SCN-*` para
  escenarios.
- Si aparece una nueva capacidad, primero decidir si es una interfaz nueva o
  una variante de una interfaz existente.
- Si cambia la UI, documentarlo despues en `docs/comfyui/interface.md`.
- Si cambia hardware, perfiles o limites, reflejarlo tambien en
  `docs/comfyui/runtime-profiles.md`.
- Si se añade una nueva variante concreta, registrarla en los manifiestos de
  `configs/comfyui/` y en los documentos de auditoria.

## Plantilla para nuevas interfaces

```md
## `UC-XXX-00` `entrada -> salida`

- Problema:
- Entradas minimas:
- Entradas opcionales:
- Salidas esperadas:
- Variantes de implementacion:
- Notas:
```

## Plantilla para nuevos escenarios

```md
## `SCN-XX`

- Objetivo:
- Interfaces implicadas:
- Prioridad:
- Restricciones:
- Resultado esperado:
```
