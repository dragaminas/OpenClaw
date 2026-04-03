from __future__ import annotations

import argparse
from typing import Iterable

from .application.session_engine import GuidedSessionEngine
from .contracts.flows import HardwareProfile
from .contracts.interaction import GuidedFlowSession, InputPrompt
from .implementations.builtin_flow_catalog import BUILTIN_FLOW_CATALOG


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Demo de sesiones guiadas para flujos de ComfyUI en OpenClaw Studio."
    )
    parser.add_argument(
        "--intent",
        help="Intencion inicial del usuario. Si se omite, se pide por stdin.",
    )
    parser.add_argument(
        "--profile",
        choices=[profile.value for profile in HardwareProfile],
        help="Perfil de hardware preferido.",
    )
    parser.add_argument(
        "--set",
        dest="preset_values",
        action="append",
        default=[],
        metavar="ENTRADA=VALOR",
        help="Prellena una entrada antes de iniciar la sesion. Se puede repetir.",
    )
    parser.add_argument(
        "--refine",
        action="store_true",
        help=(
            "Recorre tambien las entradas opcionales despues de completar las "
            "obligatorias."
        ),
    )
    return parser


def parse_preset_values(raw_values: Iterable[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_value in raw_values:
        if "=" not in raw_value:
            raise ValueError(
                f"Valor invalido para --set: {raw_value!r}. Usa ENTRADA=VALOR."
            )
        input_key, input_value = raw_value.split("=", 1)
        values[input_key.strip()] = input_value.strip()
    return values


def prompt_for_value(prompt: InputPrompt) -> str:
    print()
    print(f"[{prompt.input_key}] {prompt.prompt_text}")
    if prompt.example_values:
        print("Ejemplos:")
        for example_value in prompt.example_values:
            print(f"- {example_value}")
    if prompt.available_options:
        print("Opciones:")
        for option_label in prompt.available_options:
            print(f"- {option_label}")
    if prompt.default_value:
        print(f"Default: {prompt.default_value}")
    typed_value = input("> ").strip()
    if not typed_value and prompt.default_value is not None:
        return prompt.default_value
    return typed_value


def fill_required_inputs(
    session_engine: GuidedSessionEngine,
    session: GuidedFlowSession,
) -> None:
    while True:
        next_prompt = session_engine.build_next_required_prompt(session)
        if next_prompt is None:
            return
        typed_value = prompt_for_value(next_prompt)
        session_engine.record_input_value(
            session,
            next_prompt.input_key,
            typed_value,
        )


def fill_optional_inputs(
    session_engine: GuidedSessionEngine,
    session: GuidedFlowSession,
) -> None:
    while True:
        next_prompt = session_engine.build_next_optional_prompt(session)
        if next_prompt is None:
            return
        typed_value = prompt_for_value(next_prompt)
        if not typed_value:
            session_engine.skip_optional_input(session, next_prompt.input_key)
            continue
        session_engine.record_input_value(
            session,
            next_prompt.input_key,
            typed_value,
        )


def render_summary(
    session_engine: GuidedSessionEngine,
    session: GuidedFlowSession,
) -> str:
    summary = session_engine.build_session_summary(session)
    lines = [
        "",
        f"Flujo: {summary.flow_display_label} ({summary.use_case_id})",
        f"Variante sugerida: {summary.selected_variant_label}",
        f"Perfil de hardware: {summary.hardware_profile_label}",
        "Resumen:",
    ]
    for display_label, value in summary.provided_inputs:
        lines.append(f"- {display_label}: {value}")
    if summary.remaining_optional_inputs:
        lines.append("Opcionales aun no definidos:")
        for display_label in summary.remaining_optional_inputs:
            lines.append(f"- {display_label}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    initial_request = args.intent or input("Intencion inicial: ").strip()
    if not initial_request:
        parser.error("Hace falta una intencion inicial.")

    session_engine = GuidedSessionEngine(BUILTIN_FLOW_CATALOG)
    requested_hardware_profile = (
        HardwareProfile(args.profile)
        if args.profile
        else HardwareProfile.MINIMUM
    )

    session = session_engine.start_session(
        initial_request,
        requested_hardware_profile=requested_hardware_profile,
    )
    print(
        "Interfaz detectada: "
        f"{session.selected_flow.display_label} "
        f"({session.selected_flow.use_case_id})"
    )
    print(session.selected_flow.description)

    for input_key, input_value in parse_preset_values(args.preset_values).items():
        session_engine.record_input_value(session, input_key, input_value)

    fill_required_inputs(session_engine, session)

    if args.refine and session.remaining_optional_input_keys:
        fill_optional_inputs(session_engine, session)

    print(render_summary(session_engine, session))
    return 0
