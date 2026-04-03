# Perfiles de Hardware para Workflows de ComfyUI

Este documento implementa la tarea `8.3` del `DevPlan`.
Define como clasificar el hardware objetivo para no mezclar expectativas de
VRAM, tiempo, calidad y variantes de workflow.

## Objetivo

Sustituir la idea difusa de perfiles de ejecucion por perfiles de hardware
local.

La decision de producto es:

- el stack inicial se diseña para funcionar en el perfil `minimum`
- los perfiles `medium` y `maximum` amplian margen, no redefinen la base
- los workflows pensados para hardware superior se conservan como biblioteca de
  referencia para futuras adaptaciones

## Perfiles oficiales

| Perfil | Hardware orientativo | Rol en producto | Regla principal |
| --- | --- | --- | --- |
| `minimum` | `RTX 3060 8 GB-12 GB` | baseline operativo | todo flujo prioritario debe tener una variante viable aqui |
| `medium` | `RTX 5060-5080 12 GB-16 GB` | ampliacion gradual | puede subir calidad, duracion o lote sin cambiar la interfaz funcional |
| `maximum` | `RTX 3090-5090 24 GB-32 GB` | variantes ambiciosas y workflows base de alto VRAM | admite workflows mas pesados y sirve como destino natural para adaptaciones futuras |

## Baseline minimo

El baseline actual del producto es `minimum`.

Esto implica:

- las decisiones de UX y de captura guiada se optimizan primero para que un
  flujo pueda resolverse en `RTX 3060 8 GB-12 GB`
- las variantes `available` deberian priorizar resoluciones, duraciones y
  lotes conservadores
- la segmentacion, el fallback y la degradacion controlada son capacidades
  normales del sistema, no excepciones
- si un flujo solo existe hoy en un workflow pesado, su estado deberia ser
  `adaptable` o `future` hasta que exista una variante real para `minimum`

Referencia actual del equipo de trabajo:

- `RTX 3060 12 GB`
- `62 GiB RAM`
- `Ryzen 5 5600X`

Esa referencia sirve para perfilar el baseline, pero no debe estrechar la
definicion del perfil `minimum` a una sola GPU o a un unico equipo exacto.

## Politica para perfiles superiores

`medium` y `maximum` no bloquean el producto inicial.

Su papel por ahora es:

- permitir clasificar futuras variantes sin rehacer contratos
- separar expectativas de memoria y tiempo
- guardar workflows base mas pesados sin forzar su adopcion inmediata
- abrir una ruta clara para versiones mas ambiciosas del mismo caso de uso

## Biblioteca de workflows base

Los workflows ya presentes en `ComfyUIWorkflows/` cumplen dos funciones:

1. variantes utilizables hoy en el baseline minimo cuando sea posible
2. biblioteca base para adaptar flujos futuros a `medium` y `maximum`

Reglas:

- no sobrescribir el JSON original descargado
- documentar si un workflow es baseline-compatible o solo referencia de alto
  VRAM
- preferir derivaciones propias versionadas antes que editar la fuente original
- si un workflow pesado inspira una variante local reducida, registrar la
  relacion entre ambos

## Regla de modelado en la base Python

La capa de contratos y la aplicacion deberian usar estos tres perfiles:

- `minimum`
- `medium`
- `maximum`

Interpretacion actual:

- las variantes baseline-compatibles pueden declararse compatibles con los tres
  perfiles
- las variantes pesadas que hoy se guardan como referencia deberian apuntar al
  menos a `maximum`
- la seleccion por defecto del sistema debe caer en `minimum`

## Relacion con tareas siguientes

- `8.4` medira limites concretos del baseline `minimum`
- `8.5` auditara la biblioteca de workflows base con esta clasificacion
- `8.6` mapeara que workflow cumple papel de baseline y cual queda como
  referencia de alto VRAM
- `8.11` derivara workflows locales sin perder trazabilidad con la biblioteca
  original
