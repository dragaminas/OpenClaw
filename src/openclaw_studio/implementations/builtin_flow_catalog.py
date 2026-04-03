from __future__ import annotations

"""Built-in catalog of guided creative flows for the studio CLI demo."""

from openclaw_studio.contracts.flows import (
    ExecutionProfile,
    ExecutionVariant,
    FlowDefinition,
    FlowInputDefinition,
    ImplementationMaturity,
    InputValueType,
    OutputArtifactType,
    SelectableOption,
)


PROMPT_INPUT = FlowInputDefinition(
    input_key="prompt",
    display_label="Descripcion breve",
    prompt_text="Describe brevemente que quieres conseguir.",
    value_type=InputValueType.LONG_TEXT,
    is_required=True,
    example_values=(
        "retrato cinematografico de un explorador en una cueva azul",
        "plano corto animado con look pictorico y personaje estable",
    ),
)

BASE_IMAGE_INPUT = FlowInputDefinition(
    input_key="entrada_base",
    display_label="Imagen base",
    prompt_text="Indica la imagen base o el material visual de partida.",
    value_type=InputValueType.IMAGE,
    is_required=True,
    example_values=("frames/shot_010_start.png", "still-lookdev-base.png"),
)

BASE_VIDEO_INPUT = FlowInputDefinition(
    input_key="entrada_base",
    display_label="Video o secuencia base",
    prompt_text="Indica el video o la secuencia base que quieres procesar.",
    value_type=InputValueType.VIDEO,
    is_required=True,
    example_values=("renders/shot_010_previz.mp4", "frames/shot_010/"),
)

CHARACTER_REFERENCES_INPUT = FlowInputDefinition(
    input_key="referencias_personaje",
    display_label="Referencias de personaje",
    prompt_text="Opcional: añade referencias de personaje separadas por comas.",
    value_type=InputValueType.IMAGE_LIST,
    example_values=("refs/hero-front.png, refs/hero-side.png",),
)

STYLE_REFERENCES_INPUT = FlowInputDefinition(
    input_key="referencias_estilo",
    display_label="Referencias de estilo",
    prompt_text="Opcional: añade referencias de estilo separadas por comas.",
    value_type=InputValueType.IMAGE_LIST,
    example_values=("refs/color-board.png, refs/lighting.png",),
)

OPTIONAL_LORAS_INPUT = FlowInputDefinition(
    input_key="loras_opcionales",
    display_label="LoRAs opcionales",
    prompt_text="Opcional: indica LoRAs o perfiles de estilo separados por comas.",
    value_type=InputValueType.SHORT_TEXT,
    example_values=("lenovo-realism, hero-style-v1",),
)

VISUAL_CONTROLS_INPUT = FlowInputDefinition(
    input_key="controles_visuales",
    display_label="Controles visuales",
    prompt_text="Opcional: que controles quieres activar.",
    value_type=InputValueType.MULTI_CHOICE,
    default_value="todos",
    selectable_options=(
        SelectableOption("outline", "contorno"),
        SelectableOption("depth", "profundidad"),
        SelectableOption("pose", "pose"),
    ),
    example_values=("todos", "outline, depth", "pose"),
)

TARGET_SIZE_INPUT = FlowInputDefinition(
    input_key="tamanio_objetivo",
    display_label="Tamano objetivo",
    prompt_text="Opcional: que perfil de tamano quieres usar.",
    value_type=InputValueType.CHOICE,
    default_value="preview",
    selectable_options=(
        SelectableOption("preview", "preview"),
        SelectableOption("standard", "standard"),
        SelectableOption("high", "high"),
    ),
)

DURATION_INPUT = FlowInputDefinition(
    input_key="duracion_objetivo",
    display_label="Duracion objetivo",
    prompt_text="Opcional: indica duracion o numero de frames.",
    value_type=InputValueType.SHORT_TEXT,
    example_values=("3 segundos", "49 frames"),
)

SEGMENTATION_MODE_INPUT = FlowInputDefinition(
    input_key="modo_segmentacion",
    display_label="Modo de segmentacion",
    prompt_text="Opcional: como quieres gestionar la longitud del plano.",
    value_type=InputValueType.CHOICE,
    default_value="auto",
    selectable_options=(
        SelectableOption("auto", "auto"),
        SelectableOption("single", "sin fragmentar"),
        SelectableOption("segmented", "fragmentado"),
    ),
)

START_IMAGE_INPUT = FlowInputDefinition(
    input_key="imagen_inicial",
    display_label="Imagen inicial",
    prompt_text="Indica la imagen inicial.",
    value_type=InputValueType.IMAGE,
    is_required=True,
    example_values=("frames/keyframe_start.png",),
)

END_IMAGE_INPUT = FlowInputDefinition(
    input_key="imagen_final",
    display_label="Imagen final",
    prompt_text="Indica la imagen final.",
    value_type=InputValueType.IMAGE,
    is_required=True,
    example_values=("frames/keyframe_end.png",),
)

RENDERED_VIDEO_INPUT = FlowInputDefinition(
    input_key="video_renderizado",
    display_label="Video renderizado",
    prompt_text="Indica el video ya renderizado que quieres mejorar.",
    value_type=InputValueType.VIDEO,
    is_required=True,
    example_values=("output/shot_010_render.mp4",),
)

ENHANCEMENT_GOAL_INPUT = FlowInputDefinition(
    input_key="objetivo_mejora",
    display_label="Objetivo de mejora",
    prompt_text="Opcional: que quieres mejorar prioritariamente.",
    value_type=InputValueType.CHOICE,
    default_value="resolution",
    selectable_options=(
        SelectableOption("resolution", "resolucion"),
        SelectableOption("cleanup", "limpieza"),
        SelectableOption("finish", "acabado"),
    ),
)

STYLE_EXPLORATION_FOCUS_INPUT = FlowInputDefinition(
    input_key="foco_variacion",
    display_label="Foco de exploracion",
    prompt_text="Opcional: que quieres explorar prioritariamente.",
    value_type=InputValueType.CHOICE,
    default_value="style",
    selectable_options=(
        SelectableOption("character", "personaje"),
        SelectableOption("style", "estilo"),
        SelectableOption("finish", "acabado"),
    ),
)


BUILTIN_FLOW_CATALOG = (
    FlowDefinition(
        use_case_id="UC-IMG-01",
        display_label="Texto a imagen",
        description=(
            "Genera una imagen guiada por descripcion breve y referencias opcionales."
        ),
        output_type=OutputArtifactType.IMAGE_SET,
        sample_user_requests=(
            "quiero crear una imagen desde texto",
            "quiero generar una imagen",
        ),
        routing_phrases=("texto a imagen", "crear una imagen", "generar imagen"),
        required_input_keys=("prompt",),
        optional_input_keys=(
            "referencias_personaje",
            "referencias_estilo",
            "loras_opcionales",
            "tamanio_objetivo",
        ),
        input_definitions=(
            PROMPT_INPUT,
            CHARACTER_REFERENCES_INPUT,
            STYLE_REFERENCES_INPUT,
            OPTIONAL_LORAS_INPUT,
            TARGET_SIZE_INPUT,
        ),
        execution_variants=(
            ExecutionVariant(
                variant_id="txt2img-local-future",
                display_label="Variante local futura de texto a imagen",
                maturity=ImplementationMaturity.FUTURE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                ),
            ),
            ExecutionVariant(
                variant_id="txt2img-cloud-adaptable",
                display_label="Variante cloud adaptable",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_execution_profiles=(
                    ExecutionProfile.RUNPOD_HIGH_VRAM,
                ),
            ),
        ),
    ),
    FlowDefinition(
        use_case_id="UC-IMG-02",
        display_label="Imagen base a frame renderizado",
        description=(
            "Transforma una imagen base en un frame final con controles visuales "
            "opcionales."
        ),
        output_type=OutputArtifactType.IMAGE_SET,
        sample_user_requests=(
            "quiero crear una imagen a partir de una imagen base",
            "quiero renderizar este frame",
        ),
        routing_phrases=("imagen base", "frame renderizado", "look dev", "img2img"),
        required_input_keys=("entrada_base", "prompt"),
        optional_input_keys=(
            "referencias_personaje",
            "referencias_estilo",
            "loras_opcionales",
            "controles_visuales",
            "tamanio_objetivo",
        ),
        input_definitions=(
            BASE_IMAGE_INPUT,
            PROMPT_INPUT,
            CHARACTER_REFERENCES_INPUT,
            STYLE_REFERENCES_INPUT,
            OPTIONAL_LORAS_INPUT,
            VISUAL_CONTROLS_INPUT,
            TARGET_SIZE_INPUT,
        ),
        execution_variants=(
            ExecutionVariant(
                variant_id="z-image-turbo-local",
                display_label="Z-Image Turbo CN local",
                maturity=ImplementationMaturity.AVAILABLE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                ),
                workflow_file_references=(
                    "ComfyUIWorkflows/260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json",
                ),
            ),
            ExecutionVariant(
                variant_id="img2img-cloud",
                display_label="Batch cloud de mayor calidad",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_execution_profiles=(
                    ExecutionProfile.RUNPOD_HIGH_VRAM,
                ),
            ),
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-01",
        display_label="Video base a paquete de controles",
        description=(
            "Extrae materiales de control reutilizables desde una animacion base."
        ),
        output_type=OutputArtifactType.CONTROL_PACKAGE,
        sample_user_requests=(
            "quiero extraer controles de este video",
            "quiero preparar esta animacion para render",
        ),
        routing_phrases=("preprocess", "controles", "rough animation", "animatica"),
        required_input_keys=("entrada_base",),
        optional_input_keys=("controles_visuales", "tamanio_objetivo"),
        input_definitions=(
            BASE_VIDEO_INPUT,
            VISUAL_CONTROLS_INPUT,
            TARGET_SIZE_INPUT,
        ),
        execution_variants=(
            ExecutionVariant(
                variant_id="ai-renderer-preprocess-local",
                display_label="AI Renderer Preprocess local",
                maturity=ImplementationMaturity.AVAILABLE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                ),
                workflow_file_references=(
                    "ComfyUIWorkflows/"
                    "260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json",
                ),
            ),
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-02",
        display_label="Video base y referencias a video renderizado",
        description=(
            "Renderiza un plano animado a partir de una base y referencias "
            "visuales."
        ),
        output_type=OutputArtifactType.VIDEO,
        sample_user_requests=(
            "quiero renderizar este video",
            "quiero convertir esta animacion en un plano renderizado",
        ),
        routing_phrases=("video renderizado", "plano renderizado", "animacion base"),
        required_input_keys=("entrada_base", "prompt"),
        optional_input_keys=(
            "referencias_personaje",
            "referencias_estilo",
            "loras_opcionales",
            "controles_visuales",
            "duracion_objetivo",
            "modo_segmentacion",
        ),
        input_definitions=(
            BASE_VIDEO_INPUT,
            PROMPT_INPUT,
            CHARACTER_REFERENCES_INPUT,
            STYLE_REFERENCES_INPUT,
            OPTIONAL_LORAS_INPUT,
            VISUAL_CONTROLS_INPUT,
            DURATION_INPUT,
            SEGMENTATION_MODE_INPUT,
        ),
        execution_variants=(
            ExecutionVariant(
                variant_id="ai-renderer-local",
                display_label="AI Renderer 2.0 local",
                maturity=ImplementationMaturity.AVAILABLE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                ),
                workflow_file_references=(
                    "ComfyUIWorkflows/260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json",
                ),
            ),
            ExecutionVariant(
                variant_id="ai-renderer-runpod",
                display_label="AI Renderer 2.0 Runpod",
                maturity=ImplementationMaturity.AVAILABLE,
                supported_execution_profiles=(
                    ExecutionProfile.RUNPOD_HIGH_VRAM,
                ),
                workflow_file_references=(
                    "ComfyUIWorkflows/"
                    "260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json",
                ),
            ),
            ExecutionVariant(
                variant_id="ai-renderer-local-gguf",
                display_label="Fallback local con GGUF",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                ),
            ),
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-03",
        display_label="Imagen inicial y final a video",
        description=(
            "Genera una transicion o clip guiado por dos keyframes extremos."
        ),
        output_type=OutputArtifactType.VIDEO,
        sample_user_requests=(
            "quiero convertir estas dos imagenes en un video",
            "quiero una transicion entre dos imagenes",
        ),
        routing_phrases=("imagen inicial y final", "dos imagenes", "transicion"),
        required_input_keys=("imagen_inicial", "imagen_final", "prompt"),
        optional_input_keys=(
            "referencias_personaje",
            "referencias_estilo",
            "loras_opcionales",
            "duracion_objetivo",
        ),
        input_definitions=(
            START_IMAGE_INPUT,
            END_IMAGE_INPUT,
            PROMPT_INPUT,
            CHARACTER_REFERENCES_INPUT,
            STYLE_REFERENCES_INPUT,
            OPTIONAL_LORAS_INPUT,
            DURATION_INPUT,
        ),
        execution_variants=(
            ExecutionVariant(
                variant_id="start-to-end-adaptable",
                display_label="Variante adaptable start-to-end",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                    ExecutionProfile.RUNPOD_HIGH_VRAM,
                ),
            ),
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-04",
        display_label="Video renderizado a video mejorado",
        description=(
            "Mejora una salida de video ya generada con foco en calidad final."
        ),
        output_type=OutputArtifactType.ENHANCED_VIDEO,
        sample_user_requests=(
            "quiero mejorar este video",
            "quiero hacer upscale de este video",
        ),
        routing_phrases=("mejorar video", "upscale", "remaster"),
        required_input_keys=("video_renderizado",),
        optional_input_keys=(
            "objetivo_mejora",
            "tamanio_objetivo",
            "modo_segmentacion",
        ),
        input_definitions=(
            RENDERED_VIDEO_INPUT,
            ENHANCEMENT_GOAL_INPUT,
            TARGET_SIZE_INPUT,
            SEGMENTATION_MODE_INPUT,
        ),
        execution_variants=(
            ExecutionVariant(
                variant_id="video-upscale-local-future",
                display_label="Variante local futura de mejora de video",
                maturity=ImplementationMaturity.FUTURE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                ),
            ),
            ExecutionVariant(
                variant_id="video-upscale-cloud-future",
                display_label="Variante cloud futura de mejora de video",
                maturity=ImplementationMaturity.FUTURE,
                supported_execution_profiles=(
                    ExecutionProfile.RUNPOD_HIGH_VRAM,
                ),
            ),
        ),
    ),
    FlowDefinition(
        use_case_id="UC-IMG-03",
        display_label="Imagen o frame a variantes de estilo",
        description=(
            "Explora estilos y acabados reutilizables sobre una base visual."
        ),
        output_type=OutputArtifactType.IMAGE_SET,
        sample_user_requests=(
            "quiero explorar estilos para esta imagen",
            "quiero sacar variantes de estilo",
        ),
        routing_phrases=("variantes de estilo", "explorar estilo", "lora", "acabado"),
        required_input_keys=("entrada_base", "prompt"),
        optional_input_keys=(
            "referencias_estilo",
            "loras_opcionales",
            "foco_variacion",
        ),
        input_definitions=(
            BASE_IMAGE_INPUT,
            PROMPT_INPUT,
            STYLE_REFERENCES_INPUT,
            OPTIONAL_LORAS_INPUT,
            STYLE_EXPLORATION_FOCUS_INPUT,
        ),
        execution_variants=(
            ExecutionVariant(
                variant_id="style-variants-local",
                display_label="Exploracion local derivada de imagen a imagen",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_execution_profiles=(
                    ExecutionProfile.LOCAL_RTX3060_12GB,
                ),
            ),
            ExecutionVariant(
                variant_id="style-variants-cloud",
                display_label="Exploracion cloud en lote",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_execution_profiles=(
                    ExecutionProfile.RUNPOD_HIGH_VRAM,
                ),
            ),
        ),
    ),
)
