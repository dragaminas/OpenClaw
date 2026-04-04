from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import Runner


class RunnerNotFoundError(KeyError):
    pass


@dataclass
class RunnerRegistry:
    _runners: dict[str, Runner] = field(default_factory=dict)

    def register(self, runner: Runner) -> None:
        runner_id = runner.describe().runner_id
        self._runners[runner_id] = runner

    def get(self, runner_id: str) -> Runner | None:
        return self._runners.get(runner_id)

    def require(self, runner_id: str) -> Runner:
        runner = self.get(runner_id)
        if runner is None:
            raise RunnerNotFoundError(runner_id)
        return runner

    def list_runner_ids(self) -> list[str]:
        return sorted(self._runners)


_DEFAULT_REGISTRY: RunnerRegistry | None = None


def build_default_runner_registry() -> RunnerRegistry:
    from .comfyui import ComfyUIRunner

    registry = RunnerRegistry()
    registry.register(ComfyUIRunner())
    return registry


def get_default_runner_registry() -> RunnerRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = build_default_runner_registry()
    return _DEFAULT_REGISTRY
