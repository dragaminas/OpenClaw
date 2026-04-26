# Evaluacion de Stacks 3D para ComfyUI

Este documento implementa la tarea `9.2` del `DevPlan`.
Compara los stacks candidatos iniciales para la linea `3D` del proyecto y
cierra la decision de `MVP` para la fase 9.

## Nota de vigencia

Con corte `2026-04-18`, este documento debe leerse como registro historico de
la decision tomada para la fase 9, no como apuesta vigente e incuestionada del
producto 3D.

La evidencia posterior deja una lectura mas afinada:

- `SF3D` sirvio como baseline tecnico dentro de `ComfyUI`
- la fase 9 probo ejecucion, exportacion e importacion en `Blender`
- esa evidencia no basta por si sola para declarar calidad visual suficiente
- la linea activa a explorar a continuacion pasa a ser `Hunyuan3D` nativo, ya
  fuera de `ComfyUI`, segun `docs/hunyuan3d/phase-10-native-transition.md`

Actualizacion posterior:

- si la calidad visual de una ruta nueva dentro de `ComfyUI` supera claramente
  a `SF3D` y a la configuracion local de `Hunyuan3D`, debe reabrirse la
  decision de arquitectura
- la investigacion `Trellis2 GGUF` queda documentada en
  `docs/comfyui/trellis2-gguf-quality-investigation.md`
- con corte `2026-04-25`, la decision de esa investigacion queda en
  `no-go_provisional` hasta que el runtime aislado y el set minimo de modelos
  queden realmente instalados, segun
  `docs/comfyui/trellis2-gguf-validation-results.md`

## Corte temporal y alcance

Fecha de corte de esta evaluacion: `2026-04-12`.

La comparativa se centra en:

- `Stable Fast 3D` o `SF3D`
- `Hunyuan 3D`
- `InstantMesh`

El objetivo no es decidir "el sistema mas ambicioso", sino elegir el mejor
encaje para:

- baseline local `RTX 3060 8 GB-12 GB`
- uso desde `ComfyUI`
- futura portabilidad o dockerizacion
- handoff util hacia `Blender`
- estrategia de producto basada en `assets` reutilizables

## Criterios de evaluacion

| Criterio | Que significa aqui |
| --- | --- |
| ajuste a `MVP` | permite cerrar pronto una cadena funcional y mantenible |
| ajuste a baseline | puede convivir con `RTX 3060 8 GB-12 GB` sin exigir `24 GB+` |
| madurez en `ComfyUI` | existe una ruta razonable y de baja friccion dentro de `ComfyUI` |
| portabilidad | no obliga a un stack especialmente fragil o dificil de meter en `Docker` |
| handoff a `Blender` | el output llega en formato y estado utiles para componer |
| claridad de producto | ayuda a construir una oferta simple para usuario final |

## Resumen ejecutivo

- decision de `MVP`: la fase 9 debe apostar por `SF3D` como baseline dentro de
  `ComfyUI`
- `SF3D` gana no por ser el sistema mas ambicioso, sino por ser el mejor
  equilibrio actual entre sencillez, portabilidad, coste operativo y encaje
  con un `MVP` que debe acabar en `Blender`
- `Hunyuan 3D` sigue siendo una linea estrategicamente interesante, pero queda
  fuera del `MVP` de `ComfyUI`; si se retoma despues, deberia hacerse via repo
  oficial, `API` o addon propio, no via wrappers comunitarios de `ComfyUI`
- `InstantMesh` sigue siendo util como comparativa o proxy rapido, pero no
  mejora claramente a `SF3D` como apuesta principal de producto
- la escena compleja no debe ser el baseline de esta fase; incluso con `SF3D`,
  la estrategia correcta sigue siendo generar activos y envolventes por
  separado y componer en `Blender`

## Tabla comparativa

| Stack | Entrada nativa principal | `ComfyUI` hoy | Encaje en baseline local | Lectura de producto |
| --- | --- | --- | --- | --- |
| `SF3D` | `single image -> mesh` | ruta natural y ligera dentro de `ComfyUI` | alto | mejor candidato para el `MVP` |
| `Hunyuan 3D` | familia con `text/image -> 3D` | posible, pero con mas friccion y wrappers comunitarios | medio o bajo para baseline local en `ComfyUI` | mejor linea futura fuera del `MVP` de `ComfyUI` |
| `InstantMesh` | `single image -> mesh` | usable como via secundaria | medio | bueno como proxy o comparativa |
| `Trellis2 GGUF` | `single/multiview image -> textured mesh` | investigacion nueva, depende de wrappers y GGUF comunitarios | no-go provisional | candidato si la calidad visual justifica la complejidad |

## `SF3D`

## Lo que aporta

- es la ruta mas simple de explicar para el `MVP`:
  `imagen -> asset 3D -> Blender`
- encaja bien con el criterio de portabilidad y futura dockerizacion
- reduce la dependencia de wrappers comunitarios o stacks de compilacion mas
  delicados
- casa bien con un producto que quiere priorizar:
  - `assets` aislados
  - muebles y props
  - personajes proxy o suficientes
  - envolventes simples o piezas de escena

## Lo que penaliza

- es `image-first`, no `text-first`
- no es la opcion mas potente si el criterio dominante son las zonas no
  visibles o la multivista avanzada
- no deberia venderse como solucion de escena compleja monolitica

## Veredicto

- mejor candidato para el `MVP` en `ComfyUI`
- mejor baseline para `UC-3D-02`
- mejor base para un puente `texto -> imagen -> 3D`

## `Hunyuan 3D`

## Lo que aporta

- ofrece una familia mas ambiciosa y rica como estrategia general
- tiene mucho sentido cuando importa de verdad la coherencia volumetrica o se
  dispone de varias vistas
- es una linea atractiva para calidad superior, `PBR` o pipelines mas serios

## Lo que penaliza para esta fase

- mete mucha mas complejidad operativa en el `MVP`
- en `ComfyUI`, la experiencia depende demasiado de wrappers comunitarios y
  dependencias auxiliares
- complica mas la historia de portabilidad y mantenimiento
- convierte facilmente el baseline local en algo friccionado o fragil

## Veredicto

- no debe ser la apuesta del `MVP` en `ComfyUI`
- si se explora despues, deberia hacerse via repo oficial de `Hunyuan3D`,
  fuera de la linea principal de esta fase

## `InstantMesh`

## Lo que aporta

- sigue siendo util para pruebas rapidas y proxies
- tiene valor como comparativa tecnica o como salida de emergencia

## Lo que penaliza

- no simplifica mas que `SF3D` el relato de producto
- no aporta una ventaja clara suficiente para desplazar a `SF3D`

## Veredicto

- se mantiene como opcion secundaria
- no deberia ser la apuesta principal de la fase

## Hipotesis por caso de uso

| Caso de uso | Hipotesis principal | Alternativa | Motivo |
| --- | --- | --- | --- |
| `UC-3D-01` `texto -> objeto/personaje` | `texto -> imagen semilla -> SF3D` | dejarlo para fase posterior si el puente no basta | para el `MVP`, importa cerrar una ruta simple y portable |
| `UC-3D-02` `imagen -> objeto/personaje` | `SF3D` | `InstantMesh` como proxy o comparativa | es el mejor cierre directo para `MVP` |
| `UC-3D-03` `texto -> set/escena` | no perseguir escena monolitica; pasar por imagen y descomponer en activos | futura linea externa | la escena completa no es baseline de esta fase |
| `UC-3D-04` `imagen -> set/escena` | descomponer referencia en piezas y envolventes usando `SF3D` por activo | `blockout` o composicion parcial | encaja mejor con el control fino que queremos en `Blender` |

## Recomendacion de producto

## Primera apuesta

- cerrar la `V1` con `SF3D`
- usar `ComfyUI` solo para lo que mas valor aporta en el `MVP`:
  - `image -> 3D`
  - `texto -> imagen -> 3D`
- reservar `Hunyuan3D` para una fase futura separada
- tratar `InstantMesh` como soporte secundario o comparativa

## Estrategia para escenas

Para interiorismo y paisajismo, la hipotesis recomendada es:

1. detectar o decidir familias de activo
2. generar por separado `envolvente`, `muebles/props` y `personajes`
3. importar todo en `Blender`
4. componer, escalar, limpiar y animar alli

La escena monolitica deberia tratarse solo como:

- benchmark de comparacion
- `blockout` rapido
- demo exploratoria

No como camino principal de producto en esta fase.

## Implicacion inmediata para la fase 9

- `9.3` y `9.4` deben modelar el baseline `3D` suponiendo `SF3D` como ruta
  inicial
- `9.6` debe centrarse en descargar y estabilizar `SF3D`, no en bloquear el
  `MVP` con `Hunyuan`
- `9.9` debe arrancar por `UC-3D-02` con `SF3D`
- `9.9.2` y `9.9.3` deben reabrirse si estaban apoyadas en workflows
  `Hunyuan`
- `9.11` debe asumir composicion en `Blender` como camino normal
- cualquier futura linea `Hunyuan3D` deberia planificarse fuera del baseline
  `ComfyUI` de esta fase
