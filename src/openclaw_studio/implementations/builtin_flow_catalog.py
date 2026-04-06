from __future__ import annotations

"""Built-in catalog of guided creative flows for the studio CLI demo."""

from openclaw_studio.contracts.flows import (
    ExecutionVariant,
    FlowDefinition,
    FlowInputDefinition,
    HardwareProfile,
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

BASELINE_COMPATIBLE_PROFILES = (
    HardwareProfile.MINIMUM,
    HardwareProfile.MEDIUM,
    HardwareProfile.MAXIMUM,
)

HIGH_VRAM_REFERENCE_PROFILES = (HardwareProfile.MAXIMUM,)


BUILTIN_FLOW_CATALOG = (
    FlowDefinition(
        use_case_id="UC-IMG-01",
        display_label="Texto a imagen",
        friendly_alias="texto-a-imagen",
        description=(
            "Genera una imagen nueva desde un prompt, con referencias opcionales "
            "de personaje o estilo. Es el flujo base para lookdev cuando todavia "
            "no existe una imagen de partida."
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
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/adaptable/"
                    "uc-img-01-text-to-image-z-image-template-v1.json",
                ),
                notes=(
                    "Semilla derivada del template local de ComfyUI para "
                    "construir la futura variante baseline.",
                ),
            ),
            ExecutionVariant(
                variant_id="txt2img-high-vram-adaptable",
                display_label="Variante adaptable basada en workflow de alto VRAM",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_hardware_profiles=HIGH_VRAM_REFERENCE_PROFILES,
                notes=(
                    "Workflow base conservado como referencia para futuras "
                    "adaptaciones a hardware superior.",
                ),
            ),
        ),
        friendly_aliases=("generar imagen", "imagen desde texto"),
    ),
    FlowDefinition(
        use_case_id="UC-IMG-02",
        display_label="Imagen base a frame renderizado",
        friendly_alias="render-frame",
        description=(
            "Toma una imagen base o frame previo y lo convierte en un frame "
            "renderizado final, manteniendo estructura con controles visuales. "
            "Sirve para pasar de previz o lookdev a un frame mas terminado."
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
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/minimum/"
                    "uc-img-02-z-image-turbo-cn-rtx3060-v1.json",
                    "ComfyUIWorkflows/"
                    "260303_MICKMUMPITZ_Z-IMAGE_TURBO_CN_1-1.json",
                ),
                notes=(
                    "La variante de producto usa la derivacion local "
                    "versionada y conserva el JSON base como referencia.",
                ),
            ),
            ExecutionVariant(
                variant_id="img2img-high-vram-reference",
                display_label="Batch adaptable basado en workflow de alto VRAM",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_hardware_profiles=HIGH_VRAM_REFERENCE_PROFILES,
                notes=(
                    "Reservado como workflow base para futuras variantes de "
                    "hardware medio o maximo.",
                ),
            ),
        ),
        friendly_aliases=(
            "render frame",
            "frame renderizado",
            "imagen renderizada",
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-01",
        display_label="Video base a paquete de controles",
        friendly_alias="prepara-video",
        description=(
            "Toma un video base o animatica y extrae materiales de control como "
            "contorno, profundidad y pose. Es el paso de preparacion antes de "
            "render-video y otros flujos que reutilizan esos controles."
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
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/minimum/"
                    "uc-vid-01-ai-renderer-preprocess-rtx3060-v1.json",
                    "ComfyUIWorkflows/"
                    "260225_MICKMUMPITZ_AI-RENDERER-PREPROCESS_1-0.json",
                ),
                notes=(
                    "La derivacion local adapta el bloque de profundidad a "
                    "DepthAnything_V2 mientras V3 no este disponible.",
                ),
            ),
        ),
        friendly_aliases=(
            "prepara video",
            "prepare-video",
            "prepare video",
            "paquete de controles",
            "controles video",
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-02",
        display_label="Video base y referencias a video renderizado",
        friendly_alias="render-video",
        description=(
            "Toma un video base, un prompt y referencias visuales para producir "
            "un plano renderizado con look final. La V1 general preserva aspect "
            "ratio, muestra el primer frame y permite activar bordes, pose y "
            "profundidad sobre la misma base."
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
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/minimum/"
                    "uc-vid-02-general-video-render-rtx3060-v1.json",
                    "ComfyUIWorkflows/local/minimum/"
                    "uc-vid-02-ai-renderer-video-rtx3060-v1.json",
                    "ComfyUIWorkflows/"
                    "260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0.json",
                ),
                notes=(
                    "La variante disponible apunta primero al workflow "
                    "derivado para baseline minimum.",
                ),
            ),
            ExecutionVariant(
                variant_id="ai-renderer-high-vram-reference",
                display_label="AI Renderer 2.0 base de alto VRAM",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_hardware_profiles=HIGH_VRAM_REFERENCE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/maximum/"
                    "uc-vid-02-ai-renderer-video-high-vram-reference-v1.json",
                    "ComfyUIWorkflows/"
                    "260225_MICKMUMPITZ_AI-RENDERER_SMPL_2-0_Runpod.json",
                ),
                notes=(
                    "Se conserva como biblioteca base para futuras adaptaciones "
                    "a hardware superior.",
                ),
            ),
            ExecutionVariant(
                variant_id="ai-renderer-local-gguf",
                display_label="Fallback local con GGUF",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
            ),
        ),
        friendly_aliases=(
            "render video",
            "video renderizado",
            "plano renderizado",
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-03",
        display_label="Imagen inicial y final a video",
        friendly_alias="transicion-video",
        description=(
            "Genera un clip de transicion entre una imagen inicial y una final, "
            "rellenando el movimiento intermedio con ayuda del prompt."
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
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/adaptable/"
                    "uc-vid-03-image-to-video-wan22-template-v1.json",
                ),
                notes=(
                    "Semilla template para construir una derivacion futura de "
                    "start-to-end.",
                ),
            ),
        ),
        friendly_aliases=(
            "transicion video",
            "dos imagenes a video",
        ),
    ),
    FlowDefinition(
        use_case_id="UC-VID-04",
        display_label="Video renderizado a video mejorado",
        friendly_alias="mejora-video",
        description=(
            "Toma un video ya renderizado y lo mejora en resolucion, limpieza o "
            "acabado final. Sirve como ultimo paso de pulido despues de "
            "render-video."
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
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/adaptable/"
                    "uc-vid-04-video-upscale-ganx4-template-v1.json",
                ),
            ),
            ExecutionVariant(
                variant_id="video-upscale-high-vram-future",
                display_label="Variante futura de alto VRAM para mejora de video",
                maturity=ImplementationMaturity.FUTURE,
                supported_hardware_profiles=HIGH_VRAM_REFERENCE_PROFILES,
            ),
        ),
        friendly_aliases=(
            "mejora video",
            "upscale video",
            "video mejorado",
        ),
    ),
    FlowDefinition(
        use_case_id="UC-IMG-03",
        display_label="Imagen o frame a variantes de estilo",
        friendly_alias="explora-estilos",
        description=(
            "Parte de una imagen o frame y genera variantes de estilo o acabado "
            "sin perder la composicion base. Es util para explorar looks antes "
            "de fijar uno."
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
                supported_hardware_profiles=BASELINE_COMPATIBLE_PROFILES,
                workflow_file_references=(
                    "ComfyUIWorkflows/local/minimum/"
                    "uc-img-03-z-image-style-exploration-rtx3060-v1.json",
                ),
                notes=(
                    "Derivacion local orientada a exploracion de estilo sobre "
                    "la base Z-Image.",
                ),
            ),
            ExecutionVariant(
                variant_id="style-variants-high-vram-reference",
                display_label="Exploracion en lote basada en workflow de alto VRAM",
                maturity=ImplementationMaturity.ADAPTABLE,
                supported_hardware_profiles=HIGH_VRAM_REFERENCE_PROFILES,
                notes=(
                    "Reservado como workflow base para futuras variantes mas "
                    "ambiciosas en hardware superior.",
                ),
            ),
        ),
        friendly_aliases=(
            "explora estilos",
            "variantes de estilo",
            "estilo imagen",
        ),
    ),
)
