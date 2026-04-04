from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any


CANONICAL_RUN_STATUSES = (
    "queued",
    "running",
    "pass",
    "soft_pass_with_fallback",
    "fail_compile",
    "fail_runtime",
    "fail_quality",
    "blocked_missing_asset",
    "cancelled",
)

ACTIVE_RUN_STATUSES = ("queued", "running")
TERMINAL_RUN_STATUSES = tuple(
    status for status in CANONICAL_RUN_STATUSES if status not in ACTIVE_RUN_STATUSES
)


@dataclass(frozen=True)
class RunnerDescription:
    runner_id: str
    display_label: str
    supported_operation_kinds: list[str]
    supported_target_kinds: list[str]
    supports_cancel: bool
    supports_progress: bool
    default_evidence_root: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunnerTarget:
    target_id: str
    display_label: str
    target_kind: str
    operation_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StartRunRequest:
    runner_id: str
    operation_kind: str
    target_id: str | None
    requested_by: str
    channel: str
    run_id: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StartRunResponse:
    runner_id: str
    operation_kind: str
    target_id: str | None
    run_id: str | None
    accepted: bool
    status: str
    message: str
    manifest_path: str | None = None
    summary_path: str | None = None
    evidence_path: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunStatus:
    runner_id: str
    operation_kind: str
    target_id: str | None
    run_id: str
    status: str
    message: str
    current_target_id: str | None = None
    manifest_path: str | None = None
    summary_path: str | None = None
    evidence_path: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunResult:
    runner_id: str
    operation_kind: str
    target_id: str | None
    run_id: str
    status: str
    message: str
    manifest_path: str | None = None
    summary_path: str | None = None
    evidence_path: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Runner(ABC):
    @abstractmethod
    def describe(self) -> RunnerDescription:
        raise NotImplementedError

    @abstractmethod
    def list_targets(self, operation_kind: str) -> list[RunnerTarget]:
        raise NotImplementedError

    @abstractmethod
    def start_run(self, request: StartRunRequest) -> StartRunResponse:
        raise NotImplementedError

    @abstractmethod
    def get_run_status(self, run_id: str) -> RunStatus:
        raise NotImplementedError

    @abstractmethod
    def cancel_run(
        self,
        run_id: str,
        *,
        requested_by: str,
        channel: str,
    ) -> RunStatus:
        raise NotImplementedError

    @abstractmethod
    def get_run_result(self, run_id: str) -> RunResult:
        raise NotImplementedError
