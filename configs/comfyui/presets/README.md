# Presets Operativos de ComfyUI

Este directorio implementa la tarea `8.14` del `DevPlan`.
Los presets no intentan sustituir toda la logica de la futura UI, pero si fijan
defaults, rutas y mensajes que la interfaz no tecnica deberia reutilizar.

## Estructura

Cada preset declara:

- `preset_id`
- `use_case_id`
- `hardware_profile`
- `workflow`
- `defaults`
- `paths`
- `user_messages`

## Regla

- si el preset apunta a un workflow en `ComfyUIWorkflows/local/`, esa es la
  variante de producto
- si apunta a un template o referencia, debe decirlo explicitamente
