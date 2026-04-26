#!/usr/bin/env python3

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args() -> tuple[str, str]:
    if "--" not in sys.argv:
        raise SystemExit("usage: blender_render_glb_preview.py -- <glb_path> <render_path>")

    dash_index = sys.argv.index("--")
    args = sys.argv[dash_index + 1 :]
    if len(args) != 2:
        raise SystemExit("usage: blender_render_glb_preview.py -- <glb_path> <render_path>")

    return args[0], args[1]


def world_bounds(mesh_objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners: list[Vector] = []
    for obj in mesh_objects:
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    mins = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    maxs = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    return mins, maxs


def point_camera_at(camera: bpy.types.Object, target: Vector) -> None:
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_preview(glb_path: str, render_path: str) -> None:
    os.makedirs(os.path.dirname(render_path), exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 960
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = render_path
    scene.render.film_transparent = False
    if hasattr(scene.eevee, "use_gtao"):
        scene.eevee.use_gtao = True
    if hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 64

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.96, 0.97, 0.99, 1.0)
    bg.inputs[1].default_value = 0.9

    bpy.ops.import_scene.gltf(filepath=glb_path)
    mesh_objects = [obj for obj in scene.objects if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError(f"No se encontraron mallas tras importar {glb_path}")

    clay = bpy.data.materials.new(name="PreviewClay")
    clay.use_nodes = True
    bsdf = clay.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.72, 0.77, 0.83, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.05
    bsdf.inputs["Roughness"].default_value = 0.55

    for obj in mesh_objects:
        obj.data.materials.clear()
        obj.data.materials.append(clay)

    mins, maxs = world_bounds(mesh_objects)
    center = (mins + maxs) / 2.0
    extents = maxs - mins
    max_dim = max(extents.x, extents.y, extents.z, 0.001)

    bpy.ops.object.light_add(type="AREA", location=(max_dim * 2.2, -max_dim * 2.6, max_dim * 2.7))
    key_light = bpy.context.active_object
    key_light.data.energy = 4500
    key_light.data.shape = "RECTANGLE"
    key_light.scale = (max_dim * 1.4, max_dim * 1.4, 1.0)
    point_camera_at(key_light, center)

    bpy.ops.object.light_add(type="AREA", location=(-max_dim * 1.8, max_dim * 1.6, max_dim * 1.8))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 1400
    fill_light.scale = (max_dim, max_dim, 1.0)
    point_camera_at(fill_light, center)

    bpy.ops.object.camera_add(
        location=(center.x + max_dim * 2.8, center.y - max_dim * 2.8, center.z + max_dim * 1.7)
    )
    camera = bpy.context.active_object
    point_camera_at(camera, center)
    scene.camera = camera

    bpy.ops.render.render(write_still=True)


def main() -> None:
    glb_path, render_path = parse_args()
    if not Path(glb_path).exists():
        raise SystemExit(f"glb no existe: {glb_path}")
    build_preview(glb_path, render_path)


main()
