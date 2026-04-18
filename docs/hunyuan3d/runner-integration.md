# Integracion de la Linea Nativa `Hunyuan3D` con Runner y Blender

Este documento implementa la tarea `10.13` del `DevPlan`.
Define como se integra la aplicacion nativa `Hunyuan3D` con el runner de
`OpenClaw`, el puente a `Blender` y los futuros puntos de automatizacion,
sin ocultar que el motor 3D corre en una aplicacion separada.

## Principio

La integracion no crea un nuevo canal.
Reutiliza el mismo registro de runners ya establecido para `ComfyUI`.

El punto de entrada canonico es:

```text
WhatsApp / CLI / futuras UIs
        |
        v
plugin studio-actions o capa de acciones seguras
        |
        v
registro de runners
        |
        v
Hunyuan3DRunner (src/openclaw_studio/runners/hunyuan3d.py)
        |
        v
servidor API de Hunyuan3D (127.0.0.1:8081)
        |
        v
glb publicado en Assets3D/
        |
        v
Blender (handoff y composicion)
```

## Runner canonico

El runner `hunyuan3d` implementa el mismo contrato `Runner` del sistema que
el runner `comfyui`.

Fichero: `src/openclaw_studio/runners/hunyuan3d.py`

`runner_id`: `hunyuan3d`

Operaciones soportadas:

- `generate_3d_asset`: lanza una corrida de inferencia 3D para un caso
  `UC-3D-01` a `UC-3D-04`
- `smoke_test`: ejecuta el script de smoke validation de la linea nativa

Targets soportados:

- `UC-3D-01`, `UC-3D-02`, `UC-3D-03`, `UC-3D-04`
- `smoke-suite`

## Registro del runner

El runner queda registrado en `build_default_runner_registry()` de
`src/openclaw_studio/runners/registry.py`:

```python
from .hunyuan3d import Hunyuan3DRunner
registry.register(Hunyuan3DRunner())
```

Esto lo hace accesible para cualquier capa del sistema: CLI, plugin de
WhatsApp, tests, etc.

## Catalogo de flujos actualizado

Los `FlowDefinition` de `UC-3D-01` a `UC-3D-04` en
`src/openclaw_studio/implementations/builtin_flow_catalog.py` ahora exponen:

- variante primaria `hunyuan3d-2mini-turbo-*` con
  `maturity=ImplementationMaturity.ADAPTABLE`
- variante `sf3d-*` degradada a `maturity=ImplementationMaturity.LEGACY`
  como benchmark secundario

## Comportamiento ante estado no instalado

Si `Hunyuan3D` no esta instalado, el runner devuelve:

```json
{
  "status": "blocked_missing_runtime",
  "message": "Hunyuan3D no está instalado. Ejecuta: bash scripts/apps/install-hunyuan3d.sh"
}
```

Este estado es legible por el plugin de WhatsApp y por el CLI.
La operadora o el administrador recibe el mensaje sin ambiguedad.

## Integracion con Blender

El runner publica el `glb` en la ruta canonica:

```text
$STUDIO_DIR/Assets3D/<project_id>/<entity_id>/hunyuan3d/output/<entity_id>__mesh__v001.glb
```

El puente a `Blender` definido en `docs/comfyui/3d-blender-bridge.md`
sigue siendo el mismo.
La unica diferencia es que el origen del `glb` ya no es
`ComfyUI/output/openclaw/uc-3d-*/` sino `Assets3D/.../hunyuan3d/output/`.

La normalizacion en `Blender` sigue el mismo canon:

- unidad: `metros`
- `up`: `+Z`
- `forward`: `-Y`
- pivot canonico segun categoria del activo

## Integracion con el plugin de WhatsApp

El plugin `studio-actions` no necesita cambios para enrutar comandos `UC-3D-*`:

- los alias `imagen-a-3d`, `texto-a-3d`, `imagen-a-escena-3d` y
  `texto-a-escena-3d` ya estan en el catalogo
- el plugin enruta al runner registrado para la aplicacion que corresponde
- si el runner `hunyuan3d` esta en el registro, la accion se delega a el
- si no esta instalado, devuelve `blocked_missing_runtime`

No hace falta cambiar el catalogo de acciones de WhatsApp ni los handlers del
plugin.

## Variables de entorno respetadas por el runner

| Variable | Valor por defecto | Uso |
| --- | --- | --- |
| `HUNYUAN3D_DIR` | `~/Hunyuan3D-2` | ruta de la instalacion |
| `HUNYUAN3D_API_URL` | `http://127.0.0.1:8081` | endpoint del servidor API |

## Puntos de automatizacion futuros

- integrar el runner con flujos de batch por `schedule` o `trigger` del sistema
- soporte para multi-asset: lanzar `UC-3D-02` multiples veces sobre una lista
  de crops y consolidar el resultado como `UC-3D-04`
- soporte para `progress` cuando el API de `Hunyuan3D` lo exponga
- wrapper de Blender addon si el addon oficial de Hunyuan3D madura

Sin embargo, ninguno de estos puntos es necesario para cerrar la fase 10.

## Relacion con otros documentos

- contrato de I/O: `docs/hunyuan3d/io-contract.md`
- interfaz operativa: `docs/hunyuan3d/interface.md`
- smoke tests: `docs/hunyuan3d/smoke-validation.md`
- runner interface canonica del sistema: `docs/architecture/runner-interface.md`
