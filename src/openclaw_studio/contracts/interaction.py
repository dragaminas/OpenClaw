from __future__ import annotations

"""Session-state contracts used by the guided interaction engine."""

from dataclasses import dataclass, field
from enum import StrEnum

from .flows import FlowDefinition, HardwareProfile


class SessionStage(StrEnum):
    """High-level state of the guided data collection process."""

    COLLECTING_REQUIRED = "collecting_required"
    COLLECTING_OPTIONAL = "collecting_optional"
    READY = "ready"


@dataclass(frozen=True)
class InputPrompt:
    """Prompt payload rendered to the user for one missing input."""

    input_key: str
    display_label: str
    prompt_text: str
    is_optional: bool
    default_value: str | None
    example_values: tuple[str, ...]
    available_options: tuple[str, ...]


@dataclass(frozen=True)
class SessionSummary:
    """Compact summary of the current session state and suggested variant."""

    use_case_id: str
    flow_display_label: str
    flow_friendly_alias: str
    selected_variant_label: str
    hardware_profile_label: str
    provided_inputs: tuple[tuple[str, str], ...]
    remaining_optional_inputs: tuple[str, ...]

    @property
    def execution_profile_label(self) -> str:
        """Backward-compatible alias during the terminology migration."""

        return self.hardware_profile_label


@dataclass
class GuidedFlowSession:
    """Mutable state collected while guiding a user through a flow."""

    session_id: str
    user_request: str
    selected_flow: FlowDefinition
    requested_hardware_profile: HardwareProfile | None = None
    stage: SessionStage = SessionStage.COLLECTING_REQUIRED
    provided_input_values: dict[str, str | tuple[str, ...]] = field(default_factory=dict)
    skipped_optional_input_keys: set[str] = field(default_factory=set)

    @property
    def requested_execution_profile(self) -> HardwareProfile | None:
        """Backward-compatible alias during the terminology migration."""

        return self.requested_hardware_profile

    @requested_execution_profile.setter
    def requested_execution_profile(self, value: HardwareProfile | None) -> None:
        """Backward-compatible alias during the terminology migration."""

        self.requested_hardware_profile = value

    @property
    def missing_required_input_keys(self) -> tuple[str, ...]:
        """Return required inputs that still need a value."""

        return tuple(
            input_key
            for input_key in self.selected_flow.required_input_keys
            if input_key not in self.provided_input_values
        )

    @property
    def remaining_optional_input_keys(self) -> tuple[str, ...]:
        """Return optional inputs that were neither answered nor skipped."""

        return tuple(
            input_key
            for input_key in self.selected_flow.optional_input_keys
            if input_key not in self.provided_input_values
            and input_key not in self.skipped_optional_input_keys
        )


# Backwards-compatible aliases kept while the rest of the project migrates.
SessionPrompt = InputPrompt
InteractionSession = GuidedFlowSession
