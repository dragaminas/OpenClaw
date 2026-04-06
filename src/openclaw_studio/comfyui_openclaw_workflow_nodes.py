from __future__ import annotations

import math
from dataclasses import dataclass


DEFAULT_FPS_TARGET = 24.0
DEFAULT_FPS_TOLERANCE = 0.01
DEFAULT_IDENTITY_SLOT_COUNT = 3
DEFAULT_SEGMENT_LENGTH_FRAMES = 49
DEFAULT_SEGMENT_OVERLAP_FRAMES = 1
DEFAULT_FINAL_TARGET_WIDTH = 1920
DEFAULT_FINAL_TARGET_HEIGHT = 1080


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


@dataclass(frozen=True)
class IdentityAnchorPlan:
    enabled_requested: bool
    effective_prompt: str
    identity_ref_count: int
    mapping_count: int
    summary: str


@dataclass(frozen=True)
class SegmentSelectionPlan:
    enabled_requested: bool
    should_segment: bool
    reason: str
    total_frame_count: int
    source_fps: float
    segment_length_frames: int
    overlap_frames: int
    segment_index: int
    segment_count: int
    segment_start_frame: int
    segment_end_frame: int
    selected_frame_count: int


@dataclass(frozen=True)
class FinalUpscalePlan:
    enabled_requested: bool
    should_resize: bool
    reason: str
    source_width: int
    source_height: int
    target_width: int
    target_height: int
    output_width: int
    output_height: int


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


def plan_segment_selection(
    *,
    total_frame_count: int,
    source_fps: float,
    enabled: bool,
    segment_length_frames: int,
    overlap_frames: int,
    segment_index: int,
) -> SegmentSelectionPlan:
    total_frames = max(int(total_frame_count), 0)
    source_rate = float(source_fps)
    segment_length = max(int(segment_length_frames), 1)
    overlap = max(int(overlap_frames), 0)
    normalized_index = max(int(segment_index), 1)
    if overlap >= segment_length:
        overlap = max(segment_length - 1, 0)

    def bypass(reason: str) -> SegmentSelectionPlan:
        return SegmentSelectionPlan(
            enabled_requested=bool(enabled),
            should_segment=False,
            reason=reason,
            total_frame_count=total_frames,
            source_fps=source_rate,
            segment_length_frames=segment_length,
            overlap_frames=overlap,
            segment_index=1,
            segment_count=1 if total_frames > 0 else 0,
            segment_start_frame=0,
            segment_end_frame=total_frames,
            selected_frame_count=total_frames,
        )

    if total_frames <= 0:
        return bypass("no_frames")
    if not enabled:
        return bypass("disabled")
    if total_frames <= segment_length:
        return bypass("clip_within_single_segment")

    stride = max(segment_length - overlap, 1)
    remaining = max(total_frames - segment_length, 0)
    segment_count = 1 + int(math.ceil(remaining / float(stride)))
    current_index = min(normalized_index, segment_count)
    start = min((current_index - 1) * stride, max(total_frames - 1, 0))
    end = min(start + segment_length, total_frames)
    selected_count = max(end - start, 0)

    return SegmentSelectionPlan(
        enabled_requested=True,
        should_segment=True,
        reason="windowed_batches",
        total_frame_count=total_frames,
        source_fps=source_rate,
        segment_length_frames=segment_length,
        overlap_frames=overlap,
        segment_index=current_index,
        segment_count=segment_count,
        segment_start_frame=start,
        segment_end_frame=end,
        selected_frame_count=selected_count,
    )


def render_segment_selection_summary(plan: SegmentSelectionPlan) -> str:
    if not plan.should_segment:
        return (
            "OpenClaw segmentation: bypass | "
            f"reason={plan.reason} | frames={plan.total_frame_count} | "
            f"fps={plan.source_fps:.3f} | segment_length={plan.segment_length_frames} | "
            f"overlap={plan.overlap_frames}"
        )
    return (
        "OpenClaw segmentation: active | "
        f"mode={plan.reason} | frames={plan.total_frame_count} | "
        f"fps={plan.source_fps:.3f} | segments={plan.segment_count} | "
        f"current={plan.segment_index}/{plan.segment_count} | "
        f"range={plan.segment_start_frame + 1}-{plan.segment_end_frame} | "
        f"selected={plan.selected_frame_count} | overlap={plan.overlap_frames}"
    )


def _normalize_even_dimension(value: float, *, fallback: int) -> int:
    rounded = int(round(float(value)))
    rounded = max(2, rounded)
    if rounded % 2 != 0:
        rounded += 1
    return max(2, rounded or fallback)


def plan_final_upscale(
    *,
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
    enabled: bool,
) -> FinalUpscalePlan:
    src_width = max(int(source_width), 0)
    src_height = max(int(source_height), 0)
    tgt_width = max(int(target_width), 0)
    tgt_height = max(int(target_height), 0)

    def bypass(reason: str) -> FinalUpscalePlan:
        return FinalUpscalePlan(
            enabled_requested=bool(enabled),
            should_resize=False,
            reason=reason,
            source_width=src_width,
            source_height=src_height,
            target_width=tgt_width,
            target_height=tgt_height,
            output_width=src_width,
            output_height=src_height,
        )

    if src_width <= 0 or src_height <= 0:
        return bypass("invalid_source_dimensions")
    if not enabled:
        return bypass("disabled")
    if tgt_width <= 0 or tgt_height <= 0:
        return bypass("invalid_target_dimensions")

    scale = min(tgt_width / float(src_width), tgt_height / float(src_height))
    output_width = _normalize_even_dimension(src_width * scale, fallback=src_width)
    output_height = _normalize_even_dimension(src_height * scale, fallback=src_height)

    if output_width == src_width and output_height == src_height:
        return bypass("target_matches_source")

    return FinalUpscalePlan(
        enabled_requested=True,
        should_resize=True,
        reason="fit_inside_target_box",
        source_width=src_width,
        source_height=src_height,
        target_width=tgt_width,
        target_height=tgt_height,
        output_width=output_width,
        output_height=output_height,
    )


def render_final_upscale_summary(plan: FinalUpscalePlan) -> str:
    if not plan.should_resize:
        return (
            "OpenClaw final upscale: bypass | "
            f"reason={plan.reason} | source={plan.source_width}x{plan.source_height} | "
            f"target={plan.target_width}x{plan.target_height}"
        )
    return (
        "OpenClaw final upscale: active | "
        f"mode={plan.reason} | source={plan.source_width}x{plan.source_height} | "
        f"target={plan.target_width}x{plan.target_height} | "
        f"output={plan.output_width}x{plan.output_height}"
    )


def _normalize_identity_text(value: object) -> str:
    return str(value or "").strip()


def _build_identity_anchor_lines(
    *,
    color_1: str,
    entity_1: str,
    color_2: str,
    entity_2: str,
    color_3: str,
    entity_3: str,
) -> list[str]:
    lines: list[str] = []
    for color, entity in (
        (color_1, entity_1),
        (color_2, entity_2),
        (color_3, entity_3),
    ):
        normalized_color = _normalize_identity_text(color)
        normalized_entity = _normalize_identity_text(entity)
        if not normalized_color and not normalized_entity:
            continue
        if normalized_color and normalized_entity:
            lines.append(f"{normalized_color} -> {normalized_entity}")
        elif normalized_color:
            lines.append(f"{normalized_color} -> entidad pendiente")
        else:
            lines.append(normalized_entity)
    return lines


def plan_identity_anchor_prompt(
    *,
    base_prompt: str,
    enabled: bool,
    total_ref_images: int,
    color_1: str = "",
    entity_1: str = "",
    color_2: str = "",
    entity_2: str = "",
    color_3: str = "",
    entity_3: str = "",
) -> IdentityAnchorPlan:
    normalized_prompt = _normalize_identity_text(base_prompt)
    total_images = max(int(total_ref_images), 0)
    identity_ref_count = max(total_images - 1, 0)
    anchor_lines = _build_identity_anchor_lines(
        color_1=color_1,
        entity_1=entity_1,
        color_2=color_2,
        entity_2=entity_2,
        color_3=color_3,
        entity_3=entity_3,
    )
    mapping_count = len(anchor_lines)

    if not enabled:
        return IdentityAnchorPlan(
            enabled_requested=False,
            effective_prompt=normalized_prompt,
            identity_ref_count=identity_ref_count,
            mapping_count=mapping_count,
            summary=(
                "OpenClaw identity anchors: bypass | requested=false | "
                f"extra_refs={identity_ref_count} | mappings={mapping_count}"
            ),
        )

    guidance_lines = [
        "Preserve stable character and object identity across the shot.",
    ]
    if anchor_lines:
        guidance_lines.append("Resolved identity anchors:")
        guidance_lines.extend(f"- {line}" for line in anchor_lines)
    else:
        guidance_lines.append(
            "Treat any color-coded or position-described subjects in the source clip "
            "as persistent identity anchors."
        )
    if identity_ref_count > 0:
        guidance_lines.append(
            "Use the attached reference images as explicit identity anchors for those subjects."
        )

    effective_prompt = normalized_prompt
    prompt_suffix = "\n".join(guidance_lines).strip()
    if prompt_suffix:
        if effective_prompt:
            effective_prompt = f"{effective_prompt}\n\n{prompt_suffix}"
        else:
            effective_prompt = prompt_suffix

    if anchor_lines:
        summary_detail = " ; ".join(anchor_lines)
        summary = (
            "OpenClaw identity anchors: active | requested=true | "
            f"extra_refs={identity_ref_count} | mappings={mapping_count} | "
            f"resolved={summary_detail}"
        )
    else:
        summary = (
            "OpenClaw identity anchors: active | requested=true | "
            f"extra_refs={identity_ref_count} | mappings=0 | "
            "resolved=generic_color_or_positional_identity_guidance"
        )

    return IdentityAnchorPlan(
        enabled_requested=True,
        effective_prompt=effective_prompt,
        identity_ref_count=identity_ref_count,
        mapping_count=mapping_count,
        summary=summary,
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


class OpenClawIdentityPromptBuilder:
    CATEGORY = "OpenClaw/video"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "BOOLEAN", "INT", "INT", "STRING")
    RETURN_NAMES = (
        "prompt",
        "enabled",
        "identity_ref_count",
        "mapping_count",
        "summary",
    )
    DESCRIPTION = (
        "Construye una capa visible de identidad opcional para el workflow de video "
        "general, uniendo prompt base, resumen color->entidad y conteo de referencias."
    )

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, object]]:
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": ""}),
                "enabled": ("BOOLEAN", {"default": False}),
                "total_ref_images": (
                    "INT",
                    {"default": 1, "min": 0, "max": 64, "step": 1},
                ),
                "color_1": ("STRING", {"default": "", "multiline": False}),
                "entity_1": ("STRING", {"default": "", "multiline": False}),
                "color_2": ("STRING", {"default": "", "multiline": False}),
                "entity_2": ("STRING", {"default": "", "multiline": False}),
                "color_3": ("STRING", {"default": "", "multiline": False}),
                "entity_3": ("STRING", {"default": "", "multiline": False}),
            }
        }

    def build(
        self,
        base_prompt: str,
        enabled: bool,
        total_ref_images: int,
        color_1: str,
        entity_1: str,
        color_2: str,
        entity_2: str,
        color_3: str,
        entity_3: str,
    ):
        plan = plan_identity_anchor_prompt(
            base_prompt=base_prompt,
            enabled=enabled,
            total_ref_images=total_ref_images,
            color_1=color_1,
            entity_1=entity_1,
            color_2=color_2,
            entity_2=entity_2,
            color_3=color_3,
            entity_3=entity_3,
        )
        return (
            plan.effective_prompt,
            plan.enabled_requested,
            plan.identity_ref_count,
            plan.mapping_count,
            plan.summary,
        )


class OpenClawSegmentSelector:
    CATEGORY = "OpenClaw/video"
    FUNCTION = "select"
    RETURN_TYPES = ("IMAGE", "BOOLEAN", "INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = (
        "images",
        "segmentation_active",
        "segment_count",
        "segment_start_frame",
        "segment_end_frame",
        "selected_frame_count",
        "summary",
    )
    DESCRIPTION = (
        "Selecciona una subseccion temporal visible del clip cargado. Si la "
        "segmentacion no aplica, devuelve el batch completo sin tocarlo."
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
                "enabled": ("BOOLEAN", {"default": False}),
                "segment_length_frames": (
                    "INT",
                    {"default": DEFAULT_SEGMENT_LENGTH_FRAMES, "min": 1, "max": 4096, "step": 1},
                ),
                "overlap_frames": (
                    "INT",
                    {"default": DEFAULT_SEGMENT_OVERLAP_FRAMES, "min": 0, "max": 1024, "step": 1},
                ),
                "segment_index": (
                    "INT",
                    {"default": 1, "min": 1, "max": 256, "step": 1},
                ),
            }
        }

    def select(
        self,
        images,
        source_fps: float,
        enabled: bool,
        segment_length_frames: int,
        overlap_frames: int,
        segment_index: int,
    ):
        original_ndim = len(images.shape)
        batched_images = images.unsqueeze(0) if original_ndim == 3 else images
        plan = plan_segment_selection(
            total_frame_count=int(batched_images.shape[0]),
            source_fps=source_fps,
            enabled=enabled,
            segment_length_frames=segment_length_frames,
            overlap_frames=overlap_frames,
            segment_index=segment_index,
        )
        summary = render_segment_selection_summary(plan)
        selected_images = batched_images
        if plan.should_segment:
            selected_images = batched_images[
                plan.segment_start_frame : plan.segment_end_frame
            ]
        if original_ndim == 3 and int(selected_images.shape[0]) == 1:
            selected_images = selected_images[0]
        return (
            selected_images,
            plan.should_segment,
            plan.segment_count,
            plan.segment_start_frame,
            plan.segment_end_frame,
            plan.selected_frame_count,
            summary,
        )


class OpenClawFinalVideoResize:
    CATEGORY = "OpenClaw/video"
    FUNCTION = "resize"
    RETURN_TYPES = ("IMAGE", "BOOLEAN", "INT", "INT", "STRING")
    RETURN_NAMES = (
        "images",
        "upscale_active",
        "output_width",
        "output_height",
        "summary",
    )
    DESCRIPTION = (
        "Reescala el render final hacia un tamano objetivo preservando aspect "
        "ratio. Funciona como equivalente local visible del paso de mejora final."
    )

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, object]]:
        return {
            "required": {
                "images": ("IMAGE",),
                "enabled": ("BOOLEAN", {"default": True}),
                "target_width": (
                    "INT",
                    {"default": DEFAULT_FINAL_TARGET_WIDTH, "min": 2, "max": 8192, "step": 2},
                ),
                "target_height": (
                    "INT",
                    {"default": DEFAULT_FINAL_TARGET_HEIGHT, "min": 2, "max": 8192, "step": 2},
                ),
            }
        }

    def resize(
        self,
        images,
        enabled: bool,
        target_width: int,
        target_height: int,
    ):
        original_ndim = len(images.shape)
        batched_images = images.unsqueeze(0) if original_ndim == 3 else images
        source_height = int(batched_images.shape[1])
        source_width = int(batched_images.shape[2])
        plan = plan_final_upscale(
            source_width=source_width,
            source_height=source_height,
            target_width=target_width,
            target_height=target_height,
            enabled=enabled,
        )
        summary = render_final_upscale_summary(plan)
        if not plan.should_resize:
            result = batched_images
        else:
            try:
                import torch
                import torch.nn.functional as F
            except ModuleNotFoundError as error:
                raise RuntimeError(
                    "OpenClaw final resize requiere torch dentro de ComfyUI."
                ) from error

            channels_first = batched_images.permute(0, 3, 1, 2).to(dtype=batched_images.dtype)
            working = channels_first.to(dtype=channels_first.dtype)
            if working.dtype not in (torch.float32, torch.float64):
                working = working.to(dtype=torch.float32)
            resized = F.interpolate(
                working,
                size=(plan.output_height, plan.output_width),
                mode="bicubic",
                align_corners=False,
            )
            result = resized.permute(0, 2, 3, 1).clamp(0.0, 1.0).to(dtype=batched_images.dtype)

        if original_ndim == 3 and int(result.shape[0]) == 1:
            result = result[0]
        return (
            result,
            plan.should_resize,
            plan.output_width,
            plan.output_height,
            summary,
        )


NODE_CLASS_MAPPINGS = {
    "OpenClawFPSInterpolation": OpenClawFPSInterpolation,
    "OpenClawIdentityPromptBuilder": OpenClawIdentityPromptBuilder,
    "OpenClawSegmentSelector": OpenClawSegmentSelector,
    "OpenClawFinalVideoResize": OpenClawFinalVideoResize,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenClawFPSInterpolation": "OpenClaw FPS Interpolation",
    "OpenClawIdentityPromptBuilder": "OpenClaw Identity Prompt Builder",
    "OpenClawSegmentSelector": "OpenClaw Segment Selector",
    "OpenClawFinalVideoResize": "OpenClaw Final Video Resize",
}


__all__ = [
    "DEFAULT_FINAL_TARGET_HEIGHT",
    "DEFAULT_FINAL_TARGET_WIDTH",
    "DEFAULT_FPS_TARGET",
    "DEFAULT_FPS_TOLERANCE",
    "DEFAULT_IDENTITY_SLOT_COUNT",
    "DEFAULT_SEGMENT_LENGTH_FRAMES",
    "DEFAULT_SEGMENT_OVERLAP_FRAMES",
    "FinalUpscalePlan",
    "FPSInterpolationPlan",
    "IdentityAnchorPlan",
    "OpenClawFinalVideoResize",
    "OpenClawFPSInterpolation",
    "OpenClawIdentityPromptBuilder",
    "OpenClawSegmentSelector",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "SegmentSelectionPlan",
    "plan_final_upscale",
    "plan_identity_anchor_prompt",
    "plan_fps_interpolation",
    "plan_segment_selection",
    "render_final_upscale_summary",
    "render_fps_interpolation_summary",
    "render_segment_selection_summary",
]
