from __future__ import annotations

"""Application service that matches requests to flows and collects inputs."""

import re
import unicodedata
import uuid
from collections.abc import Iterable

from openclaw_studio.contracts.flows import (
    ExecutionVariant,
    FlowDefinition,
    FlowInputDefinition,
    HardwareProfile,
    ImplementationMaturity,
    InputValueType,
)
from openclaw_studio.contracts.interaction import (
    GuidedFlowSession,
    InputPrompt,
    SessionStage,
    SessionSummary,
)


def normalize_text(raw_text: str) -> str:
    """Normalize free text so routing comparisons are accent-insensitive."""

    normalized_text = unicodedata.normalize("NFKD", raw_text.lower())
    ascii_text = normalized_text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip()


def tokenize(raw_text: str) -> set[str]:
    """Split normalized text into alphanumeric tokens."""

    return {
        token
        for token in re.split(r"[^a-z0-9]+", normalize_text(raw_text))
        if token
    }


class GuidedSessionEngine:
    """Coordinates flow selection and progressive input collection."""

    def __init__(self, available_flows: Iterable[FlowDefinition]):
        self.available_flows = tuple(available_flows)

    def start_session(
        self,
        user_request: str,
        requested_hardware_profile: HardwareProfile | None = None,
    ) -> GuidedFlowSession:
        """Create a new guided session for the best matching flow."""

        selected_flow = self.select_flow_for_request(user_request)
        return GuidedFlowSession(
            session_id=str(uuid.uuid4()),
            user_request=user_request,
            selected_flow=selected_flow,
            requested_hardware_profile=(
                requested_hardware_profile or HardwareProfile.MINIMUM
            ),
        )

    def select_flow_for_request(self, user_request: str) -> FlowDefinition:
        """Pick the flow whose routing phrases best match the request."""

        scored_flows = [
            (self._score_flow_match(flow_definition, user_request), flow_definition)
            for flow_definition in self.available_flows
        ]
        best_score, best_flow_definition = max(scored_flows, key=lambda item: item[0])
        if best_score <= 0:
            raise ValueError(
                "No pude identificar una interfaz funcional para esa intencion."
            )
        return best_flow_definition

    def build_next_required_prompt(
        self,
        session: GuidedFlowSession,
    ) -> InputPrompt | None:
        """Return the next unanswered required input, if any."""

        if not session.missing_required_input_keys:
            session.stage = SessionStage.READY
            return None

        next_input_key = session.missing_required_input_keys[0]
        input_definition = session.selected_flow.get_input_definition(next_input_key)
        return self._build_input_prompt(input_definition, is_optional=False)

    def build_next_optional_prompt(
        self,
        session: GuidedFlowSession,
    ) -> InputPrompt | None:
        """Return the next unanswered optional input, if any."""

        if not session.remaining_optional_input_keys:
            session.stage = SessionStage.READY
            return None

        session.stage = SessionStage.COLLECTING_OPTIONAL
        next_input_key = session.remaining_optional_input_keys[0]
        input_definition = session.selected_flow.get_input_definition(next_input_key)
        return self._build_input_prompt(input_definition, is_optional=True)

    def record_input_value(
        self,
        session: GuidedFlowSession,
        input_key: str,
        raw_value: str,
    ) -> None:
        """Store a user answer after normalizing it for the input type."""

        input_definition = session.selected_flow.get_input_definition(input_key)
        session.provided_input_values[input_key] = self._normalize_input_value(
            input_definition,
            raw_value,
        )
        session.skipped_optional_input_keys.discard(input_key)
        if (
            not session.missing_required_input_keys
            and session.stage == SessionStage.COLLECTING_REQUIRED
        ):
            session.stage = SessionStage.READY

    def skip_optional_input(
        self,
        session: GuidedFlowSession,
        input_key: str,
    ) -> None:
        """Mark an optional input as intentionally skipped."""

        if input_key in session.selected_flow.optional_input_keys:
            session.skipped_optional_input_keys.add(input_key)
        if not session.remaining_optional_input_keys:
            session.stage = SessionStage.READY

    def build_session_summary(self, session: GuidedFlowSession) -> SessionSummary:
        """Summarize the collected inputs and the chosen execution variant."""

        selected_variant = self.select_execution_variant(session)
        hardware_profile = session.requested_hardware_profile or HardwareProfile.MINIMUM

        provided_inputs: list[tuple[str, str]] = []
        for input_definition in session.selected_flow.input_definitions:
            if input_definition.input_key not in session.provided_input_values:
                continue

            stored_value = session.provided_input_values[input_definition.input_key]
            if isinstance(stored_value, tuple):
                rendered_value = ", ".join(stored_value)
            else:
                rendered_value = stored_value
            provided_inputs.append((input_definition.display_label, rendered_value))

        remaining_optional_inputs = tuple(
            session.selected_flow.get_input_definition(input_key).display_label
            for input_key in session.remaining_optional_input_keys
        )
        return SessionSummary(
            use_case_id=session.selected_flow.use_case_id,
            flow_display_label=session.selected_flow.display_label,
            selected_variant_label=selected_variant.display_label,
            hardware_profile_label=hardware_profile.value,
            provided_inputs=tuple(provided_inputs),
            remaining_optional_inputs=remaining_optional_inputs,
        )

    def select_execution_variant(
        self,
        session: GuidedFlowSession,
    ) -> ExecutionVariant:
        """Choose the best available variant for the requested hardware profile."""

        requested_hardware_profile = (
            session.requested_hardware_profile
            or HardwareProfile.MINIMUM
        )

        for execution_variant in session.selected_flow.execution_variants:
            if (
                requested_hardware_profile
                in execution_variant.supported_hardware_profiles
                and execution_variant.maturity != ImplementationMaturity.FUTURE
            ):
                return execution_variant

        for execution_variant in session.selected_flow.execution_variants:
            if execution_variant.maturity != ImplementationMaturity.FUTURE:
                return execution_variant

        return session.selected_flow.execution_variants[0]

    def _build_input_prompt(
        self,
        input_definition: FlowInputDefinition,
        is_optional: bool,
    ) -> InputPrompt:
        """Project an input definition into a user-facing prompt object."""

        return InputPrompt(
            input_key=input_definition.input_key,
            display_label=input_definition.display_label,
            prompt_text=input_definition.prompt_text,
            is_optional=is_optional,
            default_value=input_definition.default_value,
            example_values=input_definition.example_values,
            available_options=input_definition.available_option_labels(),
        )

    def _score_flow_match(
        self,
        flow_definition: FlowDefinition,
        user_request: str,
    ) -> int:
        """Score how well a flow matches the user's free-text request."""

        normalized_request = normalize_text(user_request)
        request_tokens = tokenize(user_request)
        score = 0

        for candidate_phrase in (
            flow_definition.routing_phrases
            + flow_definition.sample_user_requests
        ):
            normalized_candidate = normalize_text(candidate_phrase)
            if normalized_request == normalized_candidate:
                score += 6
                continue
            if normalized_candidate and normalized_candidate in normalized_request:
                score += 4
                continue
            candidate_tokens = tokenize(candidate_phrase)
            score += len(request_tokens & candidate_tokens)

        return score

    def _normalize_input_value(
        self,
        input_definition: FlowInputDefinition,
        raw_value: str,
    ) -> str | tuple[str, ...]:
        """Normalize a raw answer according to the expected input type."""

        trimmed_value = raw_value.strip()
        if input_definition.value_type in {
            InputValueType.SHORT_TEXT,
            InputValueType.LONG_TEXT,
            InputValueType.IMAGE,
            InputValueType.VIDEO,
        }:
            return trimmed_value

        if input_definition.value_type == InputValueType.IMAGE_LIST:
            return tuple(
                part.strip()
                for part in trimmed_value.split(",")
                if part.strip()
            )

        if input_definition.value_type == InputValueType.CHOICE:
            return self._normalize_selected_option(input_definition, trimmed_value)

        if input_definition.value_type == InputValueType.MULTI_CHOICE:
            if normalize_text(trimmed_value) in {"todos", "todo", "all"}:
                return tuple(
                    option.option_value
                    for option in input_definition.selectable_options
                )
            return tuple(
                self._normalize_selected_option(input_definition, part.strip())
                for part in trimmed_value.split(",")
                if part.strip()
            )

        return trimmed_value

    def _normalize_selected_option(
        self,
        input_definition: FlowInputDefinition,
        raw_value: str,
    ) -> str:
        """Resolve a choice answer from either the stored value or its label."""

        normalized_value = normalize_text(raw_value)
        for option in input_definition.selectable_options:
            normalized_candidates = {
                normalize_text(option.option_value),
                normalize_text(option.display_label),
            }
            if normalized_value in normalized_candidates:
                return option.option_value
        return raw_value

    # Backwards-compatible method aliases kept while callers migrate.
    match_flow = select_flow_for_request
    next_required_prompt = build_next_required_prompt
    next_optional_prompt = build_next_optional_prompt
    set_slot_value = record_input_value
    skip_optional_slot = skip_optional_input
    build_summary = build_session_summary
    select_variant = select_execution_variant


InteractiveSessionEngine = GuidedSessionEngine
