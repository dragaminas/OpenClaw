# Blender

## Estado actual

Blender ya esta integrado como primer backend creativo local.

El repo permite:

- detectar Blender
- crear proyectos nuevos
- abrir proyectos existentes
- ejecutar una smoke test real
- invocar estas acciones desde el plugin seguro de WhatsApp

## Prueba local rapida

```bash
scripts/apps/blender.sh status
scripts/apps/blender.sh smoke-test blender-smoke
```

Eso debe generar:

- un proyecto `.blend`
- un render `.png`

Por defecto quedan en:

```text
$STUDIO_DIR/BlenderProjects/<nombre>/
```

## Abrir un proyecto existente

```bash
scripts/apps/blender.sh open-project /ruta/al/proyecto.blend
```

Si no hay sesion grafica disponible, el script no intenta abrir la ventana.

## Probar el wrapper seguro

```bash
scripts/actions/blender-action.sh status
scripts/actions/blender-action.sh new castillo
scripts/actions/blender-action.sh open castillo
scripts/actions/blender-action.sh smoke-test prueba-blender
```

## Probar el puente local sin WhatsApp

```bash
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta blender"
scripts/openclaw/test-studio-actions-plugin.sh "studio crea proyecto whatsapp-demo"
```

Esto usa el mismo plugin que intercepta mensajes en WhatsApp, pero sin depender
del chat real.

## Uso esperado desde WhatsApp

Escribe a la cuenta enlazada con OpenClaw, normalmente en el chat contigo mismo:

- `studio abre blender`
- `studio como esta blender`
- `studio crea proyecto castillo`
- `studio abre proyecto castillo`
- `studio haz una prueba de blender`

Si no escribes la wake word `studio`, no deberia haber respuesta.

## Verificacion minima recomendada

1. Ejecutar `scripts/apps/blender.sh status`
2. Ejecutar `scripts/apps/blender.sh smoke-test blender-smoke`
3. Ejecutar `scripts/openclaw/test-studio-actions-plugin.sh "studio como esta blender"`
4. Confirmar que existen el `.blend` y el `.png`
