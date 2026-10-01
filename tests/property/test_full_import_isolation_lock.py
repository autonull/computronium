"""Full-tree import isolation lock: no computronium/ or packages/ module imports legacy pillars.

Phase D gate (WP44.3/D1): extends test_kernel_isolation_lock.py to cover the
entire computronium tree + all packages/, not just the kernel subpackages.

Forbidden pillar prefixes:
- autoscientist (campaign, broad_map, daemon, proposer, reasoner, literature, objectives, alerts, defects, ceec_link)
- hyperopt (analysis, comparator, comparison, _dashboard, eval_tiers, experiment, _finder, frontier, hyperparameter_metamodel, ideal_backprop, metrics, optuna_bridge, parallel_runner, portfolio, rule_frontier, scaling_law, search_space, _stats, storage)
- core.campaign (full pillar)
- execution (engine, callbacks, candidate_gen, criteria, dashboard, events, _guards, _lifecycle, lifecycle, monitoring, resources, robustness, _state, strategy, synthesizer, task, task_weights, training_dynamics, interpretability)
- lightning_ (callbacks, experiment, hpo, module, nas, strategies)
- computronium.experiments (pre-kernel layer)
- knowledge (kb-era: causal, entries, kb_cache, kb, metamodel, query, seed, surrogate, vector_store)
- leaderboard (stub)
- autopoiesis (empty stub)
- mep (CUDA, optimizers, presets)
- graph (inference, initialization, nodes, topology, training)
- papers (registry only)
- p2p.evolution (hyperopt-dependent)
- analysis (campaign/autoscientist-dependent)
- validation.core (execution._state FailureTracker/FailureRecord)
- validation.power_preregistration (FrontierRecord)
- visualization.atlas (autoscientist.objectives)
- domains.trainer (execution._guards SafetyConfig)

Shared utilities (computronium.core.logging, computronium.utils, computronium.stability.resources) are exempt.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COMPUTRONIUM_ROOT = REPO_ROOT / "computronium"
PACKAGES_ROOT = REPO_ROOT / "packages"

FORBIDDEN_PREFIXES = frozenset({
    # Legacy pillars
    "computronium.autoscientist",
    "autoscientist",
    "computronium.hyperopt",
    "hyperopt",
    "computronium.core.campaign",
    "computronium.execution",
    "computronium.lightning_",
    "lightning_",
    "computronium.experiments",
    "computronium.knowledge",
    "computronium.leaderboard",
    "computronium.autopoiesis",
    "computronium.mep",
    "computronium.graph",
    "computronium.papers",
    # Legacy submodules that import pillars (not yet repaired)
    "computronium.p2p.evolution",
    "computronium.analysis",
    "computronium.validation.core",
    "computronium.validation.power_preregistration",
    "computronium.visualization.atlas",
    # Pre-kernel flat modules
    "producer",
    "staircase",
    "probe",
    "cli",
    "param_estimator",
    "reporting",
    "report",
    "result_sink",
})

# Exempt modules that are allowed to reference pillars in docstrings or as legacy context
EXEMPT_PATHS = frozenset({
    # Phase C new files
    COMPUTRONIUM_ROOT / "validation" / "verifier.py",
    COMPUTRONIUM_ROOT / "benchmarks" / "joint",
    # packages/computronium-lab: Phase D work per A7 (rewire to kernel ModelBasedPolicy / evidence)
    PACKAGES_ROOT / "computronium-lab",
})


def _all_py_files() -> Iterator[Path]:
    # computronium/
    if COMPUTRONIUM_ROOT.exists():
        yield from sorted(COMPUTRONIUM_ROOT.rglob("*.py"))
    # packages/
    if PACKAGES_ROOT.exists():
        for pkg_dir in PACKAGES_ROOT.iterdir():
            if pkg_dir.is_dir():
                src_dir = pkg_dir / "src"
                if src_dir.exists():
                    yield from sorted(src_dir.rglob("*.py"))


def _is_exempt(path: Path) -> bool:
    for exempt in EXEMPT_PATHS:
        try:
            path.relative_to(exempt)
            return True
        except ValueError:
            pass
    return False


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
    return None


def test_full_tree_import_isolation() -> None:
    """No module in computronium/ or packages/ imports a legacy pillar."""
    violations: list[str] = []
    for path in _all_py_files():
        if path.name == "__pycache__" or "__pycache__" in str(path):
            continue
        if _is_exempt(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for mod, lineno in _imported_modules(tree):
            hit = _is_forbidden(mod)
            if hit is not None:
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{lineno}: imports {mod} ({hit})")
    assert not violations, "full-tree legacy imports:\n" + "\n".join(violations[:50])


if __name__ == "__main__":
    test_full_tree_import_isolation()
    print("Full-tree import isolation: PASS")
