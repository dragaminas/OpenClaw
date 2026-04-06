from __future__ import annotations

from dataclasses import dataclass


DEFAULT_FPS_TARGET = 24.0
DEFAULT_FPS_TOLERANCE = 0.01


@dataclass(frozen=True)
class FPSInterpolationPlan:
    enabled_requested: bool
    should_interpolate: bool
    reason: str
    source_fps: float
    target_fps: float
    output_fps: float
    source_frame_count: int
    output_frame_count: int
    inserted_frame_count: int


def plan_fps_interpolation(
    *,
    source_frame_count: int,
    source_fps: float,
    target_fps: float,
    enabled: bool,
    tolerance: float = DEFAULT_FPS_TOLERANCE,
) -> FPSInterpolationPlan:
    source_count = max(int(source_frame_count), 0)
    source_rate = float(source_fps)
    target_rate = float(target_fps)
    tol = max(float(tolerance), 0.0)

    def bypass(reason: str) -> FPSInterpolationPlan:
        return FPSInterpolationPlan(
            enabled_requested=bool(enabled),
            should_interpolate=False,
            reason=reason,
            source_fps=source_rate,
            target_fps=target_rate,
            output_fps=source_rate,
            source_frame_count=source_count,
            output_frame_count=source_count,
            inserted_frame_count=0,
        )

    if not enabled:
        return bypass("disabled")
    if source_count < 2:
        return bypass("too_few_frames")
    if source_rate <= 0:
        return bypass("invalid_source_fps")
    if target_rate <= 0:
        return bypass("invalid_target_fps")
    if abs(target_rate - source_rate) <= tol:
        return bypass("target_matches_source")
    if target_rate < source_rate:
        return bypass("target_not_above_source")

    output_frame_count = max(
        source_count,
        int(round(source_count * (target_rate / source_rate))),
    )
    inserted_frame_count = output_frame_count - source_count
    if inserted_frame_count <= 0:
        return bypass("ratio_rounds_to_source_count")

    return FPSInterpolationPlan(
        enabled_requested=True,
        should_interpolate=True,
        reason="linear_blend",
        source_fps=source_rate,
        target_fps=target_rate,
        output_fps=target_rate,
        source_frame_count=source_count,
        output_frame_count=output_frame_count,
        inserted_frame_count=inserted_frame_count,
    )


def render_fps_interpolation_summary(plan: FPSInterpolationPlan) -> str:
    if not plan.should_interpolate:
        return (
            "OpenClaw FPS interpolation: bypass | "
            f"reason={plan.reason} | source_fps={plan.source_fps:.3f} | "
            f"target_fps={plan.target_fps:.3f} | frames={plan.source_frame_count}"
        )
    return (
        "OpenClaw FPS interpolation: active | "
        f"mode={plan.reason} | source_fps={plan.source_fps:.3f} | "
        f"target_fps={plan.target_fps:.3f} | "
        f"frames={plan.source_frame_count}->{plan.output_frame_count} | "
        f"inserted={plan.inserted_frame_count}"
    )


class OpenClawFPSInterpolation:
    CATEGORY = "OpenClaw/video"
    FUNCTION = "interpolate"
    RETURN_TYPES = ("IMAGE", "FLOAT", "BOOLEAN", "INT", "STRING")
    RETURN_NAMES = (
        "images",
        "output_fps",
        "interpolated",
        "inserted_frames",
        "summary",
    )
    DESCRIPTION = (
        "Interpolacion temporal lineal para elevar FPS cuando el objetivo es "
        "mayor que el FPS base. Si el objetivo coincide o no supera al base, "
        "devuelve el batch original sin tocarlo."
    )

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, object]]:
        return {
            "required": {
                "images": ("IMAGE",),
                "source_fps": (
                    "FLOAT",
                    {"default": DEFAULT_FPS_TARGET, "min": 0.0, "max": 240.0, "step": 0.1},
                ),
                "target_fps": (
                    "FLOAT",
                    {"default": DEFAULT_FPS_TARGET, "min": 0.0, "max": 240.0, "step": 0.1},
                ),
                "enabled": ("BOOLEAN", {"default": False}),
            }
        }

    def interpolate(
        self,
        images,
        source_fps: float,
        target_fps: float,
        enabled: bool,
    ):
        plan = plan_fps_interpolation(
            source_frame_count=int(images.shape[0]),
            source_fps=source_fps,
            target_fps=target_fps,
            enabled=enabled,
        )
        summary = render_fps_interpolation_summary(plan)
        if not plan.should_interpolate:
            return images, plan.output_fps, False, 0, summary

        try:
            import torch
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "OpenClaw FPS interpolation requiere torch dentro de ComfyUI."
            ) from error

        positions = torch.linspace(
            0.0,
            float(plan.source_frame_count - 1),
            steps=plan.output_frame_count,
            device=images.device,
            dtype=torch.float32,
        )
        left = positions.floor().to(dtype=torch.long)
        right = positions.ceil().clamp(max=plan.source_frame_count - 1).to(dtype=torch.long)
        alpha = (positions - left.to(dtype=torch.float32)).to(dtype=images.dtype)
        alpha = alpha.view(-1, 1, 1, 1)

        left_images = images.index_select(0, left)
        right_images = images.index_select(0, right)
        blended = left_images * (1.0 - alpha) + right_images * alpha
        return blended, plan.output_fps, True, plan.inserted_frame_count, summary


NODE_CLASS_MAPPINGS = {
    "OpenClawFPSInterpolation": OpenClawFPSInterpolation,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenClawFPSInterpolation": "OpenClaw FPS Interpolation",
}


__all__ = [
    "DEFAULT_FPS_TARGET",
    "DEFAULT_FPS_TOLERANCE",
    "FPSInterpolationPlan",
    "OpenClawFPSInterpolation",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "plan_fps_interpolation",
    "render_fps_interpolation_summary",
]
