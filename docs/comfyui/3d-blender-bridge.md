# Puente ComfyUI -> Blender para la Linea 3D

Este documento implementa la tarea `9.12` del `DevPlan`.
Define como entra un resultado `3D` de `ComfyUI` en `Blender` y que
normalizaciones deben quedar fijadas.

## Objetivo

Hacer que `Blender` sea la segunda etapa normal de producto para:

- inspeccion
- cleanup ligero
- escala
- pivot
- materiales
- catalogacion
- composicion

## Flujo canonico

```text
ComfyUI
  -> mesh principal y metadata
  -> carpeta de imports 3D
  -> Blender
  -> normalizacion
  -> catalogo o escena
```

## Ruta sugerida

```text
$STUDIO_DIR/Assets3D/<project>/<entity_id>/
├── comfyui/output/
└── blender/
    ├── imports/
    ├── exports/
    └── catalog/
```

Regla:

- `ComfyUI` publica en `comfyui/output/`
- el bridge copia o vincula a `blender/imports/`
- `Blender` no deberia leer outputs temporales sin normalizar

## Checklist de importacion

1. importar `glb` principal
2. comprobar escala visual
3. corregir eje si hace falta
4. fijar pivot canonico
5. renombrar objeto y coleccion
6. guardar export normalizado o catalogado

## Canon despues del bridge

- unidad: `metros`
- `up`: `+Z`
- `forward`: `-Y`
- naming: `<entity_id>__mesh__v###`

## Reglas por categoria

### `objeto`

- pivot en base centrada
- escala del mundo comparable a props reales

### `personaje`

- pivot en el suelo
- origen util para rig o proxy de animacion

### `envolvente`

- origen estable para layout
- si es interior, alinear suelos y puertas antes de catalogar

## Exportaciones de salida

Despues de `Blender`, las salidas recomendadas son:

- `glb` limpio para reutilizacion
- `fbx` si otro pipeline lo necesita
- `.blend` catalogado para composicion

## Regla de producto

Un activo 3D no se considera realmente aprovechado por este sistema hasta que
ha cruzado al menos una vez por este bridge y se ha confirmado que puede
componerse o catalogarse.
