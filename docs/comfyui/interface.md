# Interfaz de Interaccion para Flujos de ComfyUI

Este documento es la fuente de verdad para la tarea `8.2` del `DevPlan`.
Define como deberia interactuar la persona usuaria con el sistema y como
representamos en codigo los flujos configurables y ejecutables.

## Objetivo

Pasar de una idea basada en scripts aislados a una base de aplicacion con
contratos, logica de negocio y capa de implementaciones, manteniendo la
experiencia principal como una sesion guiada.

## Decision de producto

La interfaz principal para flujos de ComfyUI deberia ser una sesion guiada por
pasos.

- El usuario empieza con una intencion simple.
- El sistema detecta la interfaz funcional correcta.
- El sistema pide solo los parametros que faltan.
- El sistema selecciona una variante de implementacion compatible.
- El sistema resume lo entendido antes de ejecutar.

El prompt complejo sigue existiendo, pero como modo experto y no como requisito
de entrada.

## Capas de arquitectura propuestas

La base inicial en Python queda organizada asi:

```text
src/openclaw_studio/
├── __main__.py
├── cli.py
├── contracts/
│   ├── flows.py
│   └── interaction.py
├── application/
│   └── session_engine.py
└── implementations/
    └── builtin_flow_catalog.py
```

## Responsabilidad por capa

## `contracts/`

Define contratos estables para:

- interfaces funcionales
- slots o parametros
- variantes de implementacion
- sesiones de interaccion
- prompts y resumenes

No deberia contener detalles de un workflow concreto ni logica de routing.

## `application/`

Contiene la logica de negocio:

- deteccion de interfaz funcional a partir de una intencion
- orden de captura de slots
- eleccion de la variante sugerida
- construccion del resumen de ejecucion

No deberia depender de un proveedor concreto de UI.

## `implementations/`

Contiene implementaciones concretas y catalogos adaptados al estado actual del
proyecto:

- flujos builtin ligados a los casos `UC-*`
- variantes que referencian workflows base actuales
- pistas de routing

Es la capa donde hoy se conecta el modelo funcional con los workflows reales de
Mickmumpitz y futuras variantes.

## `cli.py`

Sirve como demo operativa y herramienta de exploracion temprana.

- permite iniciar una sesion desde terminal
- pide slots obligatorios
- opcionalmente recorre refinamientos
- muestra la variante sugerida y el resumen final

## Contratos de flujo

Cada flujo configurable y ejecutable se representa como una interfaz funcional
con:

- `use_case_id`
- `label`
- `summary`
- `result_kind`
- `intent_examples`
- `routing_hints`
- `required_slot_keys`
- `optional_slot_keys`
- `slots`
- `variants`

Esto permite desacoplar:

- lo que la persona usuaria quiere hacer
- los datos que necesitamos recoger
- la implementacion concreta que se va a ejecutar

## Slots de interaccion

La captura guiada se basa en slots progresivos.

Slots ya modelados en la base inicial:

- `prompt`
- `entrada_base`
- `referencias_personaje`
- `referencias_estilo`
- `loras_opcionales`
- `controles_visuales`
- `tamanio_objetivo`
- `duracion_objetivo`
- `modo_segmentacion`
- `imagen_inicial`
- `imagen_final`
- `video_renderizado`
- `objetivo_mejora`
- `foco_variacion`

Cada slot define:

- tipo de dato
- pregunta para la sesion guiada
- ejemplos
- opciones cuando corresponda
- default si aplica

## Estados de sesion

La base inicial modela una sesion con estos estados:

1. `COLLECTING_REQUIRED`
2. `COLLECTING_OPTIONAL`
3. `READY`

Flujo esperado:

1. se detecta una interfaz funcional
2. se completan slots obligatorios
3. se ofrecen refinamientos opcionales
4. se muestra resumen
5. una capa posterior ejecutara el flujo real

## Flujos concretos ya definidos

La implementacion inicial ya define contratos para:

| ID | Flujo | Tipo | Estado |
| --- | --- | --- | --- |
| `UC-IMG-01` | Texto a imagen | Imagen | adaptable |
| `UC-IMG-02` | Imagen base a frame renderizado | Imagen | disponible |
| `UC-VID-01` | Video base a paquete de controles | Video prep | disponible |
| `UC-VID-02` | Video base y referencias a video renderizado | Video | disponible |
| `UC-VID-03` | Imagen inicial y final a video | Video | adaptable |
| `UC-VID-04` | Video renderizado a video mejorado | Video | futura variante |
| `UC-IMG-03` | Imagen o frame a variantes de estilo | Imagen | adaptable |

## Variantes de implementacion actuales

La base inicial ya se alinea con perfiles de hardware local y sugiere variantes
segun compatibilidad de hardware. Toma
`RTX 3060 8 GB-12 GB` como baseline minimo de producto.

- `Z-Image Turbo CN local`
- `AI Renderer Preprocess local`
- `AI Renderer 2.0 local`
- `AI Renderer 2.0 base de alto VRAM` para futuras
  adaptaciones
- `Fallback local con GGUF`
- variantes futuras de `texto -> imagen`
- variantes futuras de mejora de video

## Sesion guiada deseada

Ejemplo de experiencia:

1. Usuario: `quiero renderizar este video`
2. Sistema: detecta `UC-VID-02`
3. Sistema: pide video base
4. Sistema: pide descripcion breve del plano
5. Sistema: ofrece referencias visuales y controles como refinamientos
6. Sistema: propone segmentacion automatica si el plano es largo
7. Sistema: muestra resumen y variante sugerida

Esto evita exponer:

- nombres de JSON
- nombres de nodos
- detalles de ComfyUI
- prompts complejos desde el primer turno

## Regla de seleccion de variantes

La seleccion de variante deberia estar en la capa de aplicacion y usar:

- tipo de interfaz funcional
- slots completados
- perfil de hardware preferido
- madurez de la variante

La base actual ya hace una primera sugerencia en `session_engine.py`:

- prioriza variantes compatibles con el perfil de hardware pedido
- evita elegir variantes marcadas solo como `future` si hay una utilizable

## Alcance de esta implementacion

Implementado en esta `8.2`:

- documento de interfaz
- base `src/` para contratos, aplicacion e implementaciones
- catalogo builtin de flujos alineado con `8.1`
- motor inicial de sesiones guiadas
- CLI demo para probar la captura de slots

No implementado aun:

- ejecucion real de workflows desde el motor Python
- persistencia de sesiones
- integracion directa con el plugin de WhatsApp
- adaptadores UI mas alla de la CLI demo

## Comando de prueba

Desde la raiz del repo:

```bash
PYTHONPATH=src python -m openclaw_studio --intent "quiero renderizar este video" --set entrada_base=renders/shot010_previz.mp4 --set prompt="plano corto cinematico con personaje estable" --refine
```

Tambien se puede arrancar mas simple y responder por stdin:

```bash
PYTHONPATH=src python -m openclaw_studio --intent "quiero crear una imagen"
```

## Relacion con tareas posteriores

- `8.3` ya fija los perfiles de hardware y el baseline minimo de producto
- `8.5` y `8.6` aterrizaran la biblioteca de workflows base, su audit y su
  mapping real
- `8.11` conectara estas interfaces con workflows derivados locales
- `8.14` convertira estas sesiones en presets y UI operable para usuario final
