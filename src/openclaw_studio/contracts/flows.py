from __future__ import annotations

"""Immutable contracts that describe the supported creative flows."""

from dataclasses import dataclass, field
from enum import StrEnum


class InputValueType(StrEnum):
    """Types of user input the guided session knows how to capture."""

    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    IMAGE = "image"
    IMAGE_LIST = "image_list"
    VIDEO = "video"
    CHOICE = "choice"
    MULTI_CHOICE = "multi_choice"


class ExecutionProfile(StrEnum):
    """Execution environments that can run a flow variant."""

    LOCAL_RTX3060_12GB = "local-rtx3060-12gb"
    RUNPOD_HIGH_VRAM = "runpod-high-vram"


class ImplementationMaturity(StrEnum):
    """Current delivery status of a flow variant."""

    AVAILABLE = "available"
    ADAPTABLE = "adaptable"
    FUTURE = "future"


class OutputArtifactType(StrEnum):
    """Primary artifact produced by a flow."""

    IMAGE = "image"
    IMAGE_SET = "image_set"
    CONTROL_PACKAGE = "control_package"
    VIDEO = "video"
    ENHANCED_VIDEO = "enhanced_video"


@dataclass(frozen=True)
class SelectableOption:
    """One valid option for a choice-based input."""

    option_value: str
    display_label: str
    description: str = ""


@dataclass(frozen=True)
class FlowInputDefinition:
    """Definition of one user-provided input required by a flow."""

    input_key: str
    display_label: str
    prompt_text: str
    value_type: InputValueType
    help_text: str = ""
    is_required: bool = False
    default_value: str | None = None
    selectable_options: tuple[SelectableOption, ...] = ()
    example_values: tuple[str, ...] = ()

    def available_option_labels(self) -> tuple[str, ...]:
        """Return only the labels used when rendering prompt options."""

        return tuple(option.display_label for option in self.selectable_options)


@dataclass(frozen=True)
class ExecutionVariant:
    """Concrete implementation alternative for a flow."""

    variant_id: str
    display_label: str
    maturity: ImplementationMaturity
    supported_execution_profiles: tuple[ExecutionProfile, ...]
    workflow_file_references: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class FlowDefinition:
    """Complete immutable description of a guided creative flow."""

    use_case_id: str
    display_label: str
    description: str
    output_type: OutputArtifactType
    sample_user_requests: tuple[str, ...]
    routing_phrases: tuple[str, ...]
    required_input_keys: tuple[str, ...]
    optional_input_keys: tuple[str, ...]
    input_definitions: tuple[FlowInputDefinition, ...]
    execution_variants: tuple[ExecutionVariant, ...]
    notes: tuple[str, ...] = ()
    _input_definition_by_key: dict[str, FlowInputDefinition] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        """Build a lookup table so the engine can resolve inputs quickly."""

        object.__setattr__(
            self,
            "_input_definition_by_key",
            {
                input_definition.input_key: input_definition
                for input_definition in self.input_definitions
            },
        )

    def get_input_definition(self, input_key: str) -> FlowInputDefinition:
        """Return the input definition associated with a specific key."""

        return self._input_definition_by_key[input_key]


# Backwards-compatible aliases kept while the rest of the project migrates.
FieldType = InputValueType
ResultKind = OutputArtifactType
ChoiceOption = SelectableOption
SlotSpec = FlowInputDefinition
FlowVariant = ExecutionVariant
FlowInterface = FlowDefinition
