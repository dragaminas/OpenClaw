Continua en este repo con la siguiente subtarea de la fase 8: implementa 8.21.4 de forma real, no solo documental.

Contexto que debes respetar:
- Repo: OpenClaw
- 8.21.1, 8.21.2 y 8.21.3 ya estan hechas
- La V1 funcional actual del workflow general vive en:
  - ComfyUIWorkflows/local/minimum/uc-vid-02-general-video-render-rtx3060-v1.json
  - src/openclaw_studio/comfyui_general_video_v1.py
  - configs/comfyui/presets/uc-vid-02-general-video-render-v1.yaml
- La biblioteca funcional publicada en ComfyUI usa el alias `render-video`
- `studio comfyui abre workflow render-video` ya abre ese workflow funcional
- La version publicada para debug ya NO debe colapsar el camino critico en un nodo oscuro/opaco
- La version publicada para debug ya debe mostrar nodos diagnosticos visibles de fps y conteos de frames
- La rama de interpolacion FPS local ya existe, pero sigue siendo una etapa no cerrada de producto
- El fixture base para 8.15 / 8.21 sigue siendo `blenderTest.mp4`

Objetivo de esta subtarea:
- Implementar 8.21.4: soporte opcional para identidad de personajes por color
- El workflow general debe poder aceptar, de forma opcional:
  - un video base coloreado por personaje/objeto
  - una asociacion color -> personaje/objeto
  - referencias visuales por personaje asociadas a esos colores o a posiciones del personaje u objeto aclarado por un prompt, tal como se hace en los flujos bases extraidos de Mickmumpitz
- El caso base SIN colores debe seguir funcionando sin romperse

Documentacion canónica que debes leer y respetar antes de cambiar nada:
- DevPlan.md
- docs/comfyui/general-video-render-workflow.md
- docs/comfyui/interface.md
- docs/operations/comfyui.md
- docs/comfyui/e2e-validation.md
- docs/comfyui/blender-bridge.md
- docs/comfyui/whatsapp-comfyui-extension.md

Reglas de implementacion:
1. No crees una ruta paralela ajena al workflow general V1. Extiende lo existente.
2. No reviertas cambios ajenos.
3. Mantén la regla actual de debug:
   - no colapsar el camino critico en nodos opacos
   - mostrar nodos visibles y valores diagnosticos utiles
4. Si alguna parte todavia no puede resolverse bien, dejala explicitamente como limitada o pendiente, no escondida.
5. La version funcional publicada en UI debe seguir siendo la operativa, no una de validacion rapida.
6. Si introduces una capa de color, debe quedar comprensible en el canvas.
7. Si agregas nodos/flujo nuevos, deben quedar geometricamente ordenados y legibles.

Criterio funcional para 8.21.4:
- Debe existir una forma operativa de activar o desactivar la capa de personajes por color
- Debe existir una forma de mapear al menos un conjunto acotado y util de colores a referencias de personaje
- La ejecucion sin colores debe seguir funcionando igual que antes
- Debe quedar visible en el workflow:
  - si la rama de color esta activa o no
  - cuantas referencias de personaje llegaron
  - que colores/personajes se estan usando o, si no es posible literal, al menos un resumen visible del mapeo resuelto
- Debe seguir pudiendo abrirse como `render-video` desde la biblioteca `openclaw-workflows`

Haz cambios, como ubicacion esperada, en:
- src/openclaw_studio/comfyui_general_video_v1.py
- ComfyUIWorkflows/local/minimum/uc-vid-02-general-video-render-rtx3060-v1.json
- configs/comfyui/presets/uc-vid-02-general-video-render-v1.yaml
- tests/test_comfyui_general_video_v1.py
- docs/comfyui/general-video-render-workflow.md
- docs/comfyui/general-video-render-workflow-results.md si haces validacion real nueva
- cualquier otro archivo solo si de verdad hace falta y sin duplicar logica

Verificacion minima que debes ejecutar:
- python3 -m compileall src tests
- PYTHONPATH=src python3 -m unittest tests.test_comfyui_general_video_v1 tests.test_comfyui_workflow_library -v
- PYTHONPATH=src python3 -m openclaw_studio.comfyui_general_video_v1
- PYTHONPATH=src python3 -m openclaw_studio.comfyui_workflow_library sync
- al menos una comprobacion real de que el template publicado sigue abriendo `render-video`
- al menos una prueba real local con `blenderTest.mp4` o con el fixture staged equivalente
- si algo no puede correrse, explica con precision que si verificaste y que quedo bloqueado

Resultado esperado al final:
- explicar que arquitectura concreta quedo para la capa color -> personaje
- explicar que limitaciones tiene esta primera version
- dejar actualizado DevPlan/documentacion si cambia el criterio de 8.21.4
- no avanzar a 8.21.5 ni 8.21.6 salvo que 8.21.4 quede cerrada o bloqueada con evidencia clara

Importante:
- Trabaja en codigo, no te quedes en plan abstracto
- Haz cambios minimos pero solidos
- Mantén la V1 funcional y transparente
- Si haces commits, que sean estructurados
----------------------------------------------------------------------------


A battle-hardened female soldier moves through a dense jungle battlefield, tracked from behind by a close shoulder-height camera. Tense cinematic war scene. After a brief run, she stops suddenly, vigilant, as the camera arcs around her in a controlled orbit. Dramatic sunlight through foliage, dust in the air, strong silhouette, realistic tactical outfit, grounded painterly realism, coherent character design, stable motion, suspenseful atmosphere.

woman dressed like Lara Croft | central subject running forward, camera is taken her from behind, so you mostly see her back.