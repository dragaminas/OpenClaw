from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .runners import StartRunRequest, get_default_runner_registry
from .runners.registry import RunnerNotFoundError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI segura para el contrato canonico de runners."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime la respuesta en JSON.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    describe_parser = subparsers.add_parser("describe")
    describe_parser.add_argument("runner_id")

    list_targets_parser = subparsers.add_parser("list-targets")
    list_targets_parser.add_argument("runner_id")
    list_targets_parser.add_argument("operation_kind")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("runner_id")
    start_parser.add_argument("operation_kind")
    start_parser.add_argument("target_id", nargs="?")
    start_parser.add_argument("--run-id")
    start_parser.add_argument("--requested-by", default="cli")
    start_parser.add_argument("--channel", default="cli")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("runner_id")
    status_parser.add_argument("run_id")

    cancel_parser = subparsers.add_parser("cancel")
    cancel_parser.add_argument("runner_id")
    cancel_parser.add_argument("run_id")
    cancel_parser.add_argument("--requested-by", default="cli")
    cancel_parser.add_argument("--channel", default="cli")

    result_parser = subparsers.add_parser("result")
    result_parser.add_argument("runner_id")
    result_parser.add_argument("run_id")

    execute_parser = subparsers.add_parser("execute", help=argparse.SUPPRESS)
    execute_parser.add_argument("runner_id")
    execute_parser.add_argument("operation_kind")
    execute_parser.add_argument("--run-id", required=True)
    execute_parser.add_argument("--target-id")

    return parser


def serialize_payload(payload: Any) -> Any:
    if hasattr(payload, "to_dict"):
        return payload.to_dict()
    if isinstance(payload, list):
        return [serialize_payload(item) for item in payload]
    return payload


def print_payload(payload: Any, *, as_json: bool) -> None:
    serialized = serialize_payload(payload)
    if as_json:
        json.dump(serialized, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    if isinstance(serialized, dict):
        for key, value in serialized.items():
            print(f"{key}={value}")
        return

    print(serialized)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    registry = get_default_runner_registry()

    try:
        runner = registry.require(args.runner_id)
    except RunnerNotFoundError:
        payload = {
            "accepted": False,
            "status": "unsupported",
            "message": f"No existe runner registrado con runner_id={args.runner_id!r}.",
        }
        print_payload(payload, as_json=args.json)
        return 1

    try:
        if args.command == "describe":
            payload = runner.describe()
            print_payload(payload, as_json=args.json)
            return 0

        if args.command == "list-targets":
            payload = runner.list_targets(args.operation_kind)
            print_payload(payload, as_json=args.json)
            return 0

        if args.command == "start":
            request = StartRunRequest(
                runner_id=args.runner_id,
                operation_kind=args.operation_kind,
                target_id=args.target_id,
                requested_by=args.requested_by,
                channel=args.channel,
                run_id=args.run_id,
            )
            payload = runner.start_run(request)
            print_payload(payload, as_json=args.json)
            return 0

        if args.command == "status":
            payload = runner.get_run_status(args.run_id)
            print_payload(payload, as_json=args.json)
            return 0

        if args.command == "cancel":
            payload = runner.cancel_run(
                args.run_id,
                requested_by=args.requested_by,
                channel=args.channel,
            )
            print_payload(payload, as_json=args.json)
            return 0

        if args.command == "result":
            payload = runner.get_run_result(args.run_id)
            print_payload(payload, as_json=args.json)
            return 0

        execute_run = getattr(runner, "execute_run", None)
        if execute_run is None:
            payload = {
                "accepted": False,
                "status": "unsupported",
                "message": (
                    f"El runner {args.runner_id!r} no expone ejecucion interna via CLI."
                ),
            }
            print_payload(payload, as_json=args.json)
            return 2

        payload = execute_run(
            operation_kind=args.operation_kind,
            run_id=args.run_id,
            target_id=args.target_id,
        )
        print_payload(payload, as_json=args.json)
        return 0
    except FileNotFoundError as error:
        payload = {
            "accepted": False,
            "status": "fail_runtime",
            "message": str(error),
        }
        print_payload(payload, as_json=args.json)
        return 1
    except Exception as error:
        payload = {
            "accepted": False,
            "status": "fail_runtime",
            "message": f"Fallo la CLI del runner: {error}",
        }
        print_payload(payload, as_json=args.json)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
