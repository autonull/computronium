"""Kernel isolation lock: experiment kernel imports no legacy pillar module.

WP12 conformance gate (Directive 1 port-and-delete): the six kernel
subpackages (schema/evidence/execution/learning/legality/surface) must not
import legacy surfaces — autoscientist, hyperopt, lightning_, legacy
campaign/execution/validation engines, computronium_lab, ceec delegation —
nor the pre-kernel flat modules still awaiting WP12 deletion
(producer/staircase/probe/cli/param_estimator/reporting/report/result_sink).

Shared utilities (computronium.core.logging) are exempt: they are not pillars.

K10 run-scoped state lock (WP13 Definition of Done): no `global`/`nonlocal`
statements, no module-level run-state holders (RecordStore, LegalityEngine,
FixLinkageStore, ReasoningStore, ICUModel, surrogate/service/controller
instances), no module-level accumulator containers (defaultdict/Counter).
Registries, catalogs, seed data, frozen specs, and loggers are exempt by
design (§4: registries populate at import, cheap and side-effect-free).
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

KERNEL_ROOT = (
    Path(__file__).resolve().parent.parent.parent / "computronium" / "experiment"
)
KERNEL_PKGS = ("schema", "evidence", "execution", "learning", "legality", "surface")

FORBIDDEN_PREFIXES = (
    "computronium.autoscientist",
    "autoscientist",
    "computronium.hyperopt",
    "hyperopt",
    "computronium.lightning_",
    "lightning_",
    "computronium.core.campaign",
    "computronium.execution",
    "computronium.validation",
    "computronium_lab",
    "ceec",
)

PRE_KERNEL_FLAT = frozenset({
    "producer",
    "staircase",
    "probe",
    "cli",
    "param_estimator",
    "reporting",
    "report",
    "result_sink",
})

STATEFUL_HOLDERS = frozenset({
    "RecordStore",
    "ArtifactStore",
    "LegalityEngine",
    "FixLinkageStore",
    "ReasoningStore",
    "ICUModel",
    "SurrogatePolicy",
    "GaussianProcessSurrogate",
    "ServiceLoop",
    "ServiceManager",
    "RunController",
    "PipelineRunner",
    "EvidenceDrivenAllocator",
})


def _kernel_files() -> Iterator[Path]:
    for pkg in KERNEL_PKGS:
        pkgdir = KERNEL_ROOT / pkg
        assert pkgdir.is_dir(), f"kernel package missing: {pkgdir}"
        yield from sorted(pkgdir.glob("*.py"))


def _imported_modules(tree: ast.Module) -> Iterator[tuple[str, int]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, node.lineno
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module, node.lineno


def _is_forbidden(mod: str) -> str | None:
    for prefix in FORBIDDEN_PREFIXES:
        if mod == prefix or mod.startswith(prefix + "."):
            return prefix
    if mod == "computronium.experiment" or mod.startswith("computronium.experiment."):
        tail = (
            mod[len("computronium.experiment.") :]
            if mod != "computronium.experiment"
            else ""
        )
        head = tail.split(".", 1)[0]
        if head in PRE_KERNEL_FLAT:
            return f"computronium.experiment.{head}"
    return None


class TestKernelImportIsolation:
    def test_no_legacy_pillar_imports(self) -> None:
        """No kernel module imports a legacy pillar or pre-kernel flat module."""
        violations: list[str] = []
        for path in _kernel_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for mod, lineno in _imported_modules(tree):
                hit = _is_forbidden(mod)
                if hit is not None:
                    violations.append(f"{path.name}:{lineno}: imports {mod} ({hit})")
        assert not violations, "kernel→legacy imports:\n" + "\n".join(violations)

    def test_no_legacy_filesystem_references(self) -> None:
        """No kernel module reaches into legacy pillar directories on disk."""
        needles = ("autoscientist", "hyperopt", "lightning_", "computronium_lab")
        violations: list[str] = []
        for path in _kernel_files():
            for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                stripped = line.strip()
                if stripped.startswith(("#", '"""', "Implements")):
                    continue
                if any(n in line for n in needles) and (
                    "Path" in line or "/" in line or ".json" in line
                ):
                    violations.append(f"{path.name}:{lineno}: {stripped[:100]}")
        assert not violations, "kernel→legacy filesystem reach-ins:\n" + "\n".join(
            violations
        )


class TestRunScopedState:
    def test_no_global_statements(self) -> None:
        """K10: no global/nonlocal mutation in kernel packages."""
        violations: list[str] = []
        for path in _kernel_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Global, ast.Nonlocal)):
                    violations.append(f"{path.name}:{node.lineno}: {node.names}")
        assert not violations, "global/nonlocal statements:\n" + "\n".join(violations)

    def test_no_module_level_state_holders(self) -> None:
        """K10: no module-level run-state holder instances or accumulators."""
        violations: list[str] = []
        for path in _kernel_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                    continue
                value = node.value
                if value is None or not isinstance(value, ast.Call):
                    continue
                func = value.func
                name = (
                    func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
                )
                if name in STATEFUL_HOLDERS or name in {"defaultdict", "Counter"}:
                    targets: list[str] = []
                    if isinstance(node, ast.Assign):
                        targets = [
                            t.id for t in node.targets if isinstance(t, ast.Name)
                        ]
                    else:
                        assert isinstance(node.target, ast.Name)
                        targets = [node.target.id]
                    violations.append(
                        f"{path.name}:{node.lineno}: {targets} = {name}(...)"
                    )
        assert not violations, "module-level state holders:\n" + "\n".join(violations)

    def test_engine_singleton_removed(self) -> None:
        """L10 follow-through: the legality ENGINE global stays deleted."""
        import computronium.experiment.legality.engine as engine_mod

        assert not hasattr(engine_mod, "ENGINE"), "ENGINE global reintroduced"
        assert not hasattr(engine_mod, "get_engine"), "get_engine reintroduced"

    def test_fix_linkage_global_removed(self) -> None:
        """L10 follow-through: the failure linkage globals stay deleted."""
        import computronium.experiment.evidence.failure as failure_mod

        for name in (
            "_FIX_LINKAGES",
            "link_fix_to_pattern",
            "get_fixes_for_pattern",
            "verify_fix",
            "get_unfixed_patterns",
        ):
            assert not hasattr(failure_mod, name), f"{name} reintroduced"
        assert hasattr(failure_mod, "FixLinkageStore"), "FixLinkageStore missing"

    def test_fix_linkage_store_is_run_scoped(self) -> None:
        """Two FixLinkageStore instances share no state."""
        from computronium.experiment.evidence.failure import FixLinkageStore

        first, second = FixLinkageStore(), FixLinkageStore()
        first.link_fix("p1", "abc", "fix it")
        assert len(first.fixes_for_pattern("p1")) == 1
        assert second.fixes_for_pattern("p1") == []
        assert first.verify_fix("p1", "abc", ["rec-1"])
        assert first.fixes_for_pattern("p1")[0].verified
        assert not second.verify_fix("p1", "abc", ["rec-1"])
