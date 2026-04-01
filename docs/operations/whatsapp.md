# WhatsApp

## Modelo de uso actual

`OpenClaw` no aparece como un contacto separado llamado `OpenClaw`.

La cuenta de WhatsApp enlazada pertenece al propio operador y el uso esperado es
desde el chat contigo mismo o desde el remitente explicitamente permitido por la
configuracion de OpenClaw.

## Wake word

La wake word actual es:

- `studio`

Regla:

- si el mensaje no empieza con `studio`, no deberia haber respuesta

Despues de `studio`, el lenguaje puede ser natural y simple.

## Ejemplos que deberian funcionar

- `studio abre blender`
- `studio como esta blender`
- `studio crea proyecto castillo`
- `studio abre proyecto castillo`
- `studio haz una prueba de blender`

## Que pasa sin wake word

En el canal WhatsApp configurado:

- el plugin local consume el mensaje en silencio
- el mensaje no pasa al agente general
- el sistema no deberia contestar nada

## Verificacion local antes de probar el chat real

```bash
scripts/openclaw/install-studio-actions-plugin.sh apply
scripts/openclaw/test-studio-actions-plugin.sh "studio como esta blender"
scripts/openclaw/test-studio-actions-plugin.sh "studio crea proyecto whatsapp-demo"
openclaw plugins inspect studio-actions --json
```

## Troubleshooting

Si responde sin wake word:

1. verifica que `studio-actions` este cargado
2. reinicia `openclaw-gateway.service` y `openclaw-node.service`
3. vuelve a probar el driver local y luego el chat real

Comandos utiles:

```bash
systemctl --user restart openclaw-gateway.service openclaw-node.service
scripts/doctor/openclaw-status.sh
openclaw plugins inspect studio-actions --json
```

## Nota de parsing

En mensajes reales de WhatsApp, OpenClaw puede entregar el texto al plugin
envuelto en metadatos multilinea. El parser actual ya contempla ese caso y
busca la wake word dentro del contenido real del usuario.
