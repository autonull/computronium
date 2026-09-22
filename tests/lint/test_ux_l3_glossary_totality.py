"""UX-L3: Glossary totality lock.

Every UI string key used in Explorer register must resolve in glossary.json.
No unregistered technical terms in Explorer copy.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest


def _load_glossary_keys() -> set[str]:
    """Load all registered glossary keys from glossary.json."""
    glossary_path = Path("computronium/ui/glossary.json")
    raw = json.loads(glossary_path.read_text(encoding="utf-8"))
    return set(raw.get("terms", {}).keys())


def _extract_tr_calls(source: str) -> list[str]:
    """Extract all tr() and tr_both() calls from Python source.

    Returns list of string literal keys passed as first argument.
    Only catches calls to the glossary service functions, not arbitrary .get() calls.
    """
    tree = ast.parse(source)
    keys: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                # Only catch tr/get on glossary_service instance, not dict.get()
                if isinstance(node.func.value, ast.Name):
                    func_name = node.func.attr

            # Only catch glossary service functions: tr(), tr_both(), svc.get()
            if func_name in ("tr", "tr_both") and node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Constant) and isinstance(
                    first_arg.value, str
                ):
                    keys.append(first_arg.value)
            elif func_name == "get" and node.args:
                # Check if this is a call on a glossary service instance
                if isinstance(node.func, ast.Attribute) and isinstance(
                    node.func.value, ast.Name
                ):
                    var_name = node.func.value.id
                    # Common glossary service variable names
                    if var_name in (
                        "svc",
                        "service",
                        "glossary",
                        "get_glossary_service()",
                    ):
                        first_arg = node.args[0]
                        if isinstance(first_arg, ast.Constant) and isinstance(
                            first_arg.value, str
                        ):
                            keys.append(first_arg.value)

    return keys


def _scan_ui_modules() -> dict[str, list[str]]:
    """Scan all UI modules for tr() calls and return file -> keys mapping."""
    ui_root = Path("computronium/ui")
    results: dict[str, list[str]] = {}

    for py_file in ui_root.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        source = py_file.read_text(encoding="utf-8")
        keys = _extract_tr_calls(source)
        if keys:
            rel = py_file.relative_to(ui_root).as_posix()
            results[rel] = keys

    return results


class TestGlossaryTotality:
    """UX-L3: All UI string keys must exist in glossary.json."""

    @pytest.fixture(scope="class")
    def glossary_keys(self) -> set[str]:
        return _load_glossary_keys()

    @pytest.fixture(scope="class")
    def ui_tr_calls(self) -> dict[str, list[str]]:
        return _scan_ui_modules()

    def test_all_tr_keys_exist_in_glossary(
        self, glossary_keys: set[str], ui_tr_calls: dict[str, list[str]]
    ) -> None:
        """Every tr() key must be registered in glossary.json."""
        missing: dict[str, list[str]] = {}

        for file, keys in ui_tr_calls.items():
            for key in keys:
                if key not in glossary_keys:
                    missing.setdefault(file, []).append(key)

        assert not missing, "Unregistered glossary keys found:\n" + "\n".join(
            f"  {f}: {', '.join(ks)}" for f, ks in missing.items()
        )

    def test_glossary_has_no_unused_keys(
        self, glossary_keys: set[str], ui_tr_calls: dict[str, list[str]]
    ) -> None:
        """Warn about glossary keys never used in UI code (informational)."""
        used_keys = set()
        for keys in ui_tr_calls.values():
            used_keys.update(keys)

        unused = glossary_keys - used_keys
        if unused:
            pytest.skip(
                f"Glossary has {len(unused)} unused keys (informational): "
                f"{', '.join(sorted(unused))[:200]}..."
            )

    def test_no_hardcoded_technical_terms_in_explorer_strings(self) -> None:
        """Scan glossary.json explorer strings for unregistered technical terms.

        Technical terms that should be glossaried (as whole words).
        """
        glossary_path = Path("computronium/ui/glossary.json")
        raw = json.loads(glossary_path.read_text(encoding="utf-8"))
        terms = raw.get("terms", {})

        # Known technical terms that must be glossaried (whole word match)
        technical_terms = {
            "pareto",
            "spectral",
            "lyapunov",
            "backprop",
            "gradient",
            "epoch",
            "batch",
            "accuracy",
            "loss",
            "deficit",
            "void",
            "quarantine",
            "diverged",
            "flops",
            "latency",
            "throughput",
            "walltime",
            "parameter",
            "seed",
            "ruler",
            "credit",
            "dynamics",
            "update",
            "topology",
            "geometry",
            "plasticity",
            "substrate",
            "consolidation",
            "settle",
            "horizon",
            "energy_minimization",
            "predictive",
            "instantaneous",
            "spike",
            "diffusion",
            "thermodynamic",
            "local_goodness",
            "target_inversion",
            "temporal_trace",
            "homeostatic",
            "euclidean",
            "riemannian",
            "natural_gradient",
            "elastic",
            "memristive",
            "neuromorphic",
            "photonic",
            "quantum",
            "feedforward",
            "recurrent",
            "attractor",
            "tile",
            "mesh",
            "fabric",
            "spatial",
            "lattice",
            "ntm",
            "nca",
            "routing",
            "fast_weight",
            "rule_state",
            "closed_form",
            "temporal_psi",
            "cell",
            "burst",
            "campaign",
            "knowledge",
            "structural",
            "runtime",
            "defect",
            "unquarantine",
            "maturity",
            "ceec",
            "experiment",
            "evidence",
            "belief",
            "gate",
            "decision",
            "stability",
            "plasticity",
            "ratio",
            "efficiency",
            "fog",
            "coverage",
            "badge",
            "quest",
            "record",
            "constitution",
            "causality",
            "dag",
            "passivity",
            "bound",
            "resource",
            "ceiling",
            "protocol",
            "conformance",
            "recursion",
            "invariant",
            "lineage",
            "probe",
            "stagnation",
            "genome",
            "mutation",
            "veto",
            "episode",
            "auto_evolve",
            "preview",
            "falsification",
            "ontology",
            "axis",
            "primitive",
            "system",
            "coordinate",
            "compatibility",
            "diversity",
            "novelty",
            "stratum",
            "repeat",
            "pressure",
            "cost",
            "projection",
            "projected",
            "remaining",
            "liveness",
            "heartbeat",
            "daemon",
            "continuous",
            "discovery",
            "broad",
        }

        glossary_keys_lower = {k.lower() for k in terms}
        # Also check if term is a substring of any glossary key (e.g., "stability" in "stability_plasticity_ratio")
        glossary_key_substrings = set()
        for k in glossary_keys_lower:
            parts = k.split("_")
            glossary_key_substrings.update(parts)

        violations: list[tuple[str, str, str]] = []

        for key, entry in terms.items():
            explorer = entry.get("explorer", "").lower()
            for term in technical_terms:
                # Skip if the term itself is a glossary key or part of one
                if term in glossary_keys_lower or term in glossary_key_substrings:
                    continue
                # Whole word match using word boundaries
                import re

                if re.search(rf"\b{re.escape(term)}\b", explorer):
                    violations.append((key, entry.get("explorer", ""), term))

        assert not violations, (
            f"Explorer strings contain {len(violations)} unregistered technical terms:\n"
            + "\n".join(f"  {k}: '{e}' contains '{t}'" for k, e, t in violations[:20])
        )


class TestGlossaryCoverage:
    """Additional glossary coverage checks."""

    def test_glossary_json_valid(self) -> None:
        """glossary.json must be valid JSON with required structure."""
        glossary_path = Path("computronium/ui/glossary.json")
        raw = json.loads(glossary_path.read_text(encoding="utf-8"))

        assert "version" in raw
        assert "terms" in raw
        assert isinstance(raw["terms"], dict)

        for key, entry in raw["terms"].items():
            assert "explorer" in entry, f"Key '{key}' missing 'explorer' register"
            assert "lab" in entry, f"Key '{key}' missing 'lab' register"
            assert isinstance(entry["explorer"], str)
            assert isinstance(entry["lab"], str)

    def test_glossary_keys_snake_case(self) -> None:
        """All glossary keys should be snake_case."""
        glossary_keys = _load_glossary_keys()
        for key in glossary_keys:
            assert re.fullmatch(r"[a-z][a-z0-9_]*", key), f"Key '{key}' not snake_case"

    def test_explorer_strings_readable_length(self) -> None:
        """Explorer strings should be reasonably short (≤200 chars)."""
        glossary_path = Path("computronium/ui/glossary.json")
        raw = json.loads(glossary_path.read_text(encoding="utf-8"))

        long_strings = []
        for key, entry in raw["terms"].items():
            explorer = entry.get("explorer", "")
            if len(explorer) > 200:
                long_strings.append((key, len(explorer)))

        assert not long_strings, (
            f"Explorer strings too long (>200 chars): {long_strings[:5]}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
