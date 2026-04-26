#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch
import trimesh
from PIL import Image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ejecuta shape generation de Hunyuan3D con parametros reproducibles."
    )
    parser.add_argument("--repo-dir", required=True, help="Ruta local al repo clonado Hunyuan3D-2.")
    parser.add_argument("--input-image", required=True, help="Imagen de entrada.")
    parser.add_argument("--output-glb", required=True, help="Ruta del GLB de salida.")
    parser.add_argument("--stats-json", required=True, help="Ruta del JSON de estadisticas.")
    parser.add_argument("--model-path", required=True, help="Repo/modelo HF a usar.")
    parser.add_argument("--subfolder", required=True, help="Subfolder del modelo shape.")
    parser.add_argument("--device", default="cuda", help="Dispositivo para inferencia.")
    parser.add_argument("--seed", type=int, default=42, help="Seed fija para la corrida.")
    parser.add_argument("--num-inference-steps", type=int, default=30, help="Pasos de inferencia.")
    parser.add_argument("--guidance-scale", type=float, default=5.0, help="CFG / guidance scale.")
    parser.add_argument("--octree-resolution", type=int, default=256, help="Resolucion de octree.")
    parser.add_argument(
        "--enable-flashvdm",
        action="store_true",
        help="Activa FlashVDM cuando el pipeline lo soporte.",
    )
    parser.add_argument(
        "--skip-background-removal",
        action="store_true",
        help="No ejecutar removal de fondo antes de la inferencia.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    repo_dir = Path(args.repo_dir).expanduser().resolve()
    input_image = Path(args.input_image).expanduser().resolve()
    output_glb = Path(args.output_glb).expanduser().resolve()
    stats_json = Path(args.stats_json).expanduser().resolve()

    if not repo_dir.exists():
        raise SystemExit(f"repo-dir no existe: {repo_dir}")
    if not input_image.exists():
        raise SystemExit(f"input-image no existe: {input_image}")

    sys.path.insert(0, str(repo_dir))

    from hy3dgen.rembg import BackgroundRemover
    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline

    output_glb.parent.mkdir(parents=True, exist_ok=True)
    stats_json.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(input_image).convert("RGBA")
    if not args.skip_background_removal:
        image = BackgroundRemover()(image)

    try:
        pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            args.model_path,
            subfolder=args.subfolder,
            use_safetensors=True,
            device=args.device,
        )
    except FileNotFoundError as exc:
        # Algunos repositorios, como Hunyuan3D-2.1, exponen el checkpoint
        # principal como .ckpt y no como .safetensors. Reintentamos sin romper
        # el flujo para los modelos que sí usan safetensors.
        if ".safetensors" not in str(exc):
            raise
        print(
            "Falling back to checkpoint loading without safetensors "
            f"for {args.model_path}/{args.subfolder}",
            file=sys.stderr,
        )
        pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            args.model_path,
            subfolder=args.subfolder,
            use_safetensors=False,
            device=args.device,
        )
    if args.enable_flashvdm:
        pipeline.enable_flashvdm(mc_algo="mc")

    generator = torch.Generator(args.device).manual_seed(args.seed)

    start_time = time.time()
    with torch.inference_mode():
        mesh = pipeline(
            image=image,
            generator=generator,
            octree_resolution=args.octree_resolution,
            num_inference_steps=args.num_inference_steps,
            guidance_scale=args.guidance_scale,
            mc_algo="mc",
        )[0]
    duration_seconds = time.time() - start_time

    mesh.export(output_glb)
    exported = trimesh.load(output_glb, force="mesh")

    stats = {
        "repo_dir": str(repo_dir),
        "input_image": str(input_image),
        "output_glb": str(output_glb),
        "model_path": args.model_path,
        "subfolder": args.subfolder,
        "device": args.device,
        "seed": args.seed,
        "num_inference_steps": args.num_inference_steps,
        "guidance_scale": args.guidance_scale,
        "octree_resolution": args.octree_resolution,
        "enable_flashvdm": args.enable_flashvdm,
        "skip_background_removal": args.skip_background_removal,
        "duration_seconds": round(duration_seconds, 3),
        "glb_bytes": output_glb.stat().st_size,
        "vertices": int(len(exported.vertices)),
        "faces": int(len(exported.faces)),
        "is_watertight": bool(exported.is_watertight),
        "bounding_box_extents": [float(value) for value in exported.bounding_box.extents],
    }

    stats_json.write_text(json.dumps(stats, indent=2, sort_keys=True))
    print(json.dumps(stats, indent=2, sort_keys=True))

    if args.device.startswith("cuda") and torch.cuda.is_available():
        torch.cuda.empty_cache()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
