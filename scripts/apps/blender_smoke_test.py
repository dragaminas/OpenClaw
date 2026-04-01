import bpy
import os
import sys
import traceback
from pathlib import Path


DEBUG_LOG = Path("/tmp/openclaw-blender-smoke-python.log")


def build_scene(blend_path: str, render_path: str) -> None:
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    os.makedirs(os.path.dirname(render_path), exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = render_path

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.8))
    cube = bpy.context.active_object
    cube.scale = (1.0, 1.0, 1.4)
    cube.rotation_euler = (0.3, 0.2, 0.5)

    material = bpy.data.materials.new(name="SmokeMaterial")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.11, 0.52, 0.84, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.15
    bsdf.inputs["Roughness"].default_value = 0.35
    cube.data.materials.clear()
    cube.data.materials.append(material)

    bpy.ops.object.light_add(type="AREA", location=(2.5, -2.0, 3.5))
    light = bpy.context.active_object
    light.rotation_euler = (0.8, 0.1, 0.8)
    light.data.energy = 3000

    bpy.ops.object.camera_add(location=(3.8, -3.2, 2.6), rotation=(1.1, 0.0, 0.85))
    camera = bpy.context.active_object
    scene.camera = camera

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    try:
        if "--" not in sys.argv:
            raise SystemExit("usage: blender_smoke_test.py -- <blend_path> <render_path>")

        dash_index = sys.argv.index("--")
        args = sys.argv[dash_index + 1 :]
        if len(args) != 2:
            raise SystemExit("usage: blender_smoke_test.py -- <blend_path> <render_path>")

        blend_path, render_path = args
        DEBUG_LOG.write_text(f"blend_path={blend_path}\nrender_path={render_path}\n")
        build_scene(blend_path, render_path)
    except Exception:
        DEBUG_LOG.write_text(traceback.format_exc())
        raise


main()
