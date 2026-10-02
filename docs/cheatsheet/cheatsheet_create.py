"""Generate the Computronium architecture cheat-sheet.

Collects live architecture facts by code reflection (kernel axis
registries, config schemas, task/CLI/stage/policy catalogs, registry
counts) and renders two artifacts:

* ``docs/cheatsheet/cheatsheet.svg`` -- a directed architecture graph: a
  coarse outer flow (entry -> tasks/kernel -> ontology -> system ->
  training -> evidence -> surface) whose panels are themselves small
  directed graphs (nested insets of primitives, pipeline stages, config
  fields, and the training loop).
* ``docs/cheatsheet/cheatsheet.txt`` -- the same content as a structured
  datafile.

The layout is fully content-driven: chip/step/panel sizes and canvas
dimensions are computed from the reflected data; style constants live
in one :class:`Style` object. Re-running after code changes regenerates
both artifacts in a single execution; no source file outside this
script is touched.

Usage::

    uv run python docs/cheatsheet/cheatsheet_create.py [--check]
"""

from __future__ import annotations

import argparse
import ast
import dataclasses
import datetime
import inspect
import re
import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import] — only `git rev-parse`, local read-only call
import xml.etree.ElementTree as ET  # ruff: ignore[suspicious-xml-etree-import,suspicious-xml-element-tree-usage] — parses our own generated SVG, never untrusted input
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
OUT_SVG = HERE / "cheatsheet.svg"
OUT_TXT = HERE / "cheatsheet.txt"

# ---------------------------------------------------------------------------
# 1. Reflection: pull the architecture facts out of the live codebase
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Primitive:
    name: str
    description: str
    available: bool
    reason: str | None


@dataclass(frozen=True, slots=True)
class Stage:
    key: str
    label: str
    summary: str


@dataclass(frozen=True, slots=True)
class Policy:
    key: str
    class_name: str
    summary: str


@dataclass(frozen=True, slots=True)
class Bundle:
    axes: dict[str, tuple[Primitive, ...]]
    configs: dict[str, tuple[str, ...]]
    api_symbols: tuple[str, ...]
    cli: tuple[tuple[str, str], ...]
    demos: tuple[tuple[str, str], ...]
    gallery: tuple[str, ...]
    domains: tuple[str, ...]
    tasks: dict[str, tuple[str, ...]]
    stages: tuple[Stage, ...]
    policies: tuple[Policy, ...]
    objectives: tuple[tuple[str, bool], ...]
    priors: tuple[str, ...]
    capabilities: int
    constraints: int
    policies_registry: int
    verification: tuple[str, ...]
    run_spec_fields: tuple[str, ...]
    record_fields: tuple[str, ...]
    store_methods: tuple[str, ...]
    packages: tuple[str, ...]
    history_metrics: tuple[str, ...]
    extra_metrics: tuple[str, ...]
    schema_version: int
    commit: str


def _fields(cls: type) -> tuple[str, ...]:
    if dataclasses.is_dataclass(cls):
        return tuple(f.name for f in dataclasses.fields(cls))
    if hasattr(cls, "model_fields"):
        return tuple(cls.model_fields)
    return tuple(getattr(cls, "__annotations__", {}))


def _cli_commands() -> tuple[tuple[str, str], ...]:
    tree = ast.parse((ROOT / "computronium" / "cli" / "__main__.py").read_text())
    ordered: tuple[str, ...] = ()
    summaries: dict[str, str] = {}
    for node in tree.body:
        value: ast.expr | None = None
        name: str | None = None
        if isinstance(node, ast.Assign):
            value = node.value
            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in {"_SUBCOMMANDS", "_SUMMARIES"}
            ):
                name = node.targets[0].id
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            value = node.value
            if isinstance(node.target, ast.Name) and node.target.id in {
                "_SUBCOMMANDS",
                "_SUMMARIES",
            }:
                name = node.target.id
        if value is None or name is None or not isinstance(value, ast.Dict):
            continue
        pairs = [
            (k.value, v.value)
            for k, v in zip(value.keys, value.values, strict=True)
            if isinstance(k, ast.Constant)
            and isinstance(v, ast.Constant)
            and isinstance(k.value, str)
            and isinstance(v.value, str)
        ]
        if name == "_SUBCOMMANDS":
            ordered = tuple(
                k.value
                for k in value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)
            )
        else:
            summaries = dict(pairs)
    return tuple((cmd, summaries.get(cmd, "")) for cmd in ordered)


def _demos() -> tuple[tuple[str, str], ...]:
    out: list[tuple[str, str]] = []
    for path in sorted((ROOT / "scripts" / "demos").glob("demo_*.py")):
        tree = ast.parse(path.read_text())
        doc = ast.get_docstring(tree) or ""
        line = next(
            (raw for raw in doc.splitlines() if raw.strip().startswith("Expected:")), ""
        )
        if not line:
            line = next((raw for raw in doc.splitlines() if raw.strip()), "")
        out.append((path.stem, line.strip()[:68]))
    return tuple(out)


def _gallery_keys() -> tuple[str, ...]:
    tree = ast.parse(
        (ROOT / "computronium" / "visualization" / "gallery.py").read_text()
    )
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if (
            value is not None
            and isinstance(value, ast.Dict)
            and any(isinstance(t, ast.Name) and t.id == "DEMOS" for t in targets)
        ):
            return tuple(
                k.value
                for k in value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)
            )
    return ()


def _stage_label(key: str) -> str:
    m = re.match(r"s(\d+)_(\w+)", key)
    return f"S{m.group(1)} {m.group(2)}" if m else key


def _tasks() -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    from computronium.domains import _DOMAIN_REGISTRY

    src = (ROOT / "computronium" / "domains" / "registry.py").read_text()
    match = re.search(r"SUPPORTED_TASKS.*?=\s*frozenset\(\{(.*?)\}\)", src, re.S)
    if match is None:
        raise RuntimeError("SUPPORTED_TASKS block not found in domains/registry.py")
    group_map = {
        "vision": "vision",
        "language": "lm",
        "rl": "rl",
        "graph": "graph",
        "tabular": "tabular",
    }
    groups: dict[str, list[str]] = {}
    current = "other"
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            word = stripped.lstrip("# ").split(" ")[0].lower()
            current = group_map.get(word, word)
            continue
        for name in re.findall(r"['\"](\w+)['\"]", stripped):
            groups.setdefault(current, []).append(name)
    return tuple(_DOMAIN_REGISTRY), {k: tuple(v) for k, v in groups.items()}


def collect() -> Bundle:
    import computronium
    from computronium.core.system_trainer import SystemTrainerConfig
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.policy import POLICY_CATALOG
    from computronium.experiment.execution.stage import STAGE_REGISTRY
    from computronium.experiment.schema import metrics as kernel_metrics
    from computronium.experiment.schema import seed_registries
    from computronium.experiment.schema.axis import AXES_REGISTRIES
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.registries import (
        CAPABILITIES_REGISTRY,
        CONSTRAINTS_REGISTRY,
        POLICIES_REGISTRY,
    )
    from computronium.experiment.schema.run_spec import RunSpec
    from computronium.experiment.schema.versioning import current_schema_version
    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.dynamics import StateDynamicsConfig
    from computronium.ontology.geometry import GeometryConfig
    from computronium.ontology.substrate import SubstrateConfig
    from computronium.ontology.update import ParameterUpdateConfig
    from computronium.state import PlasticityConfig as StatePlasticityConfig
    from computronium.verification import VerificationLevel

    axes = {
        ax.value: tuple(
            Primitive(s.name, s.description, s.available, s.unavailable_reason)
            for s in reg
        )
        for ax, reg in AXES_REGISTRIES.items()
    }
    config_classes = {
        "SubstrateConfig": SubstrateConfig,
        "GeometryConfig": GeometryConfig,
        "StateDynamicsConfig": StateDynamicsConfig,
        "PlasticityConfig": StatePlasticityConfig,
        "CreditAssignmentConfig": CreditAssignmentConfig,
        "ParameterUpdateConfig": ParameterUpdateConfig,
        "SystemTrainerConfig": SystemTrainerConfig,
    }
    configs = {name: _fields(cls) for name, cls in config_classes.items()}
    domains, task_groups = _tasks()
    try:
        git = shutil.which("git")
        commit = "n/a"
        if git:
            commit = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] — git path resolved via shutil.which
                [git, "rev-parse", "--short", "HEAD"],
                capture_output=True,
                check=False,
                text=True,
                cwd=ROOT,
                timeout=5,
            ).stdout.strip()
    except OSError, subprocess.SubprocessError:
        commit = "n/a"
    return Bundle(
        axes=axes,
        configs=configs,
        api_symbols=tuple(computronium.__all__),
        cli=_cli_commands(),
        demos=_demos(),
        gallery=_gallery_keys(),
        domains=domains,
        tasks=task_groups,
        stages=tuple(
            Stage(
                key=str(k),
                label=_stage_label(str(k)),
                summary=(spec.description or "").strip()[:44],
            )
            for k, spec in STAGE_REGISTRY.items()
        ),
        policies=tuple(
            Policy(
                key,
                cls.__name__,
                ((inspect.getdoc(cls) or "").splitlines() or [""])[0][:40],
            )
            for key, cls in POLICY_CATALOG.items()
        ),
        objectives=tuple(
            (o.name, o.name in kernel_metrics.MEASURED_OBJECTIVES)
            for o in seed_registries.OBJECTIVES
        ),
        priors=tuple(p.name for p in seed_registries.PRIORS),
        capabilities=len(list(CAPABILITIES_REGISTRY)),
        constraints=len(list(CONSTRAINTS_REGISTRY)),
        policies_registry=len(list(POLICIES_REGISTRY)),
        verification=tuple(m.name for m in VerificationLevel),
        run_spec_fields=_fields(RunSpec),
        record_fields=_fields(Record),
        store_methods=tuple(
            m
            for m in (
                "create_run",
                "finish_run",
                "append",
                "append_with_artifacts",
                "get_record",
                "get_record_by_measurement_key",
                "query_records",
                "query_runs",
                "vector_search",
                "count_records",
                "count_achieved_seeds",
                "latest_run_id",
            )
            if hasattr(RecordStore, m)
        ),
        packages=tuple(
            d.name
            for d in sorted((ROOT / "packages").iterdir())
            if d.is_dir() and (d / "pyproject.toml").exists()
        ),
        history_metrics=tuple(sorted(kernel_metrics.HISTORY_METRICS)),
        extra_metrics=tuple(
            sorted(kernel_metrics.MEASURED_METRICS - kernel_metrics.HISTORY_METRICS)
        ),
        schema_version=current_schema_version(),
        commit=commit,
    )


# ---------------------------------------------------------------------------
# 2. Presentation model: chips, flows, boxes, panel insets
# ---------------------------------------------------------------------------

SANS = "Inter, 'Segoe UI', system-ui, -apple-system, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Consolas, monospace"

COLORS: dict[str, str] = {
    "entry": "#475569",
    "tasks": "#b45309",
    "kernel": "#6d28d9",
    "ontology": "#0e7490",
    "system": "#4338ca",
    "train": "#b91c1c",
    "evidence": "#047857",
    "surface": "#a16207",
}
AXIS_COLOR: dict[str, str] = {
    "substrate": "#ea580c",
    "geometry": "#16a34a",
    "dynamics": "#2563eb",
    "plasticity": "#9333ea",
    "credit": "#db2777",
    "update": "#0d9488",
}
AXIS_EMOJI: dict[str, str] = {
    "substrate": "🟧",
    "geometry": "🟩",
    "dynamics": "🟦",
    "plasticity": "🟪",
    "credit": "🌸",
    "update": "🧊",
}
AXIS_SYMBOL: dict[str, str] = {
    "substrate": "S",
    "geometry": "G",
    "dynamics": "D",
    "plasticity": "P",
    "credit": "C",
    "update": "U",
}
DOMAIN_EMOJI: dict[str, str] = {
    "vision": "🖼️",
    "lm": "💬",
    "rl": "🎮",
    "graph": "🕸️",
    "tabular": "📊",
    "timeseries": "⏱️",
    "scientific": "🔬",
}


def text_w(s: str, size: float) -> float:
    total = 0.0
    for ch in s:
        total += size * 1.25 if ord(ch) > 0x2190 else size * 0.56
    return total


@dataclass(frozen=True, slots=True)
class Chip:
    label: str
    sub: str | None = None
    accent: str | None = None
    enabled: bool = True
    mono: bool = False
    tooltip: str | None = None

    @property
    def w(self) -> float:
        label_w = text_w(
            self.label, STYLE.chip_font if not self.mono else STYLE.mono_font
        )
        sub_w = text_w(self.sub, STYLE.sub_font) if self.sub else 0.0
        return 18 + max(label_w, sub_w)

    @property
    def h(self) -> float:
        return 32 if self.sub else 23


@dataclass(frozen=True, slots=True)
class FlowStep:
    label: str
    sub: str | None = None
    color: str = "#475569"
    tooltip: str | None = None


@dataclass(frozen=True, slots=True)
class AxisBox:
    axis: str
    primitives: tuple[Chip, ...]
    config_name: str
    config_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChipsRow:
    label: str
    chips: tuple[Chip, ...]
    gap: float = 8.0


@dataclass(frozen=True, slots=True)
class FlowRow:
    label: str
    steps: tuple[FlowStep, ...]
    loop_back: bool = False


@dataclass(frozen=True, slots=True)
class FieldsRow:
    label: str
    text: str
    mono: bool = True


@dataclass(frozen=True, slots=True)
class TextRow:
    text: str


@dataclass(frozen=True, slots=True)
class Group:
    name: str
    chips: tuple[Chip, ...]
    accent: str | None = None


@dataclass(frozen=True, slots=True)
class GroupedChipsRow:
    label: str
    groups: tuple[Group, ...]
    gap: float = 8.0


@dataclass(frozen=True, slots=True)
class AxesRow:
    boxes: tuple[AxisBox, ...]


@dataclass(frozen=True, slots=True)
class Section:
    label: str
    rows: tuple[Row, ...]


@dataclass(frozen=True, slots=True)
class Columns:
    rows: tuple[Row, ...]
    gap: float = 20.0


@dataclass(frozen=True, slots=True)
class TableRow:
    label: str
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    mono: bool = True


Row = (
    ChipsRow
    | FlowRow
    | FieldsRow
    | TextRow
    | AxesRow
    | GroupedChipsRow
    | TableRow
    | Section
    | Columns
)


@dataclass(frozen=True, slots=True)
class Panel:
    key: str
    title: str
    rows: tuple[Row, ...]

    @property
    def color(self) -> str:
        return COLORS[self.key]


def _wrap_text(text: str, size: float, max_w: float) -> list[str]:
    words, lines, cur = text.split(" "), [], ""
    for word in words:
        candidate = f"{cur} {word}".strip()
        if text_w(candidate, size) <= max_w or not cur:
            cur = candidate
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def _fit(text: str, size: float, max_w: float) -> str:
    if text_w(text, size) <= max_w:
        return text
    while len(text) > 1 and text_w(text[:-1] + "…", size) > max_w:
        text = text[:-1]
    return text + "…"


# ---------------------------------------------------------------------------
# 3. Graph construction (presentation over the reflected Bundle)
# ---------------------------------------------------------------------------

STAGE_SHORT: dict[str, str] = {
    "s1_frame": "resolve question → objective + operating point",
    "s2_space": "axis snapshot + legality preview (dry-run safe)",
    "s3_schedule": "fidelity / seed / epoch planning",
    "s4_gate": "LegalityEngine enforcement",
    "s5_compose": "compose_joint_system bridge",
    "s6_train": "SystemTrainer settle bridge",
    "s7_measure": "objectives vs OBJECTIVES; probes",
    "s8_record": "atomic append + artifacts + embeddings",
    "s9_attribute": "counterfactual axis attribution",
    "s10_decide": "promotion predicates + allocation handoff",
    "s11_report": "surface.report fragments",
}

DOMAIN_GROUP: dict[str, str] = {
    "vision": "vision",
    "lm": "lm",
    "rl": "rl",
    "graph": "graph",
    "tabular": "tabular",
    "timeseries": "timeseries",
    "scientific": "scientific",
}

CONFIG_FOR_AXIS: dict[str, str] = {
    "substrate": "SubstrateConfig",
    "geometry": "GeometryConfig",
    "dynamics": "StateDynamicsConfig",
    "plasticity": "PlasticityConfig",
    "credit": "CreditAssignmentConfig",
    "update": "ParameterUpdateConfig",
}


def _axis_boxes(b: Bundle) -> tuple[AxisBox, ...]:
    return tuple(
        AxisBox(
            axis=axis,
            primitives=tuple(
                Chip(
                    label=p.name,
                    accent=AXIS_COLOR[axis],
                    enabled=p.available,
                    tooltip=p.description,
                )
                for p in prims
            ),
            config_name=CONFIG_FOR_AXIS[axis],
            config_fields=b.configs[CONFIG_FOR_AXIS[axis]],
        )
        for axis, prims in b.axes.items()
    )


def _entry_rows(b: Bundle) -> tuple[Row, ...]:
    cli_groups = tuple(
        Group(
            name=fname,
            chips=tuple(
                Chip(
                    label=f"comp {c}", sub=sub[:36], accent=COLORS["entry"], tooltip=sub
                )
                for c, sub in b.cli
                if c in members
            ),
        )
        for fname, members in (
            ("▶ EXECUTION", {"run", "benchmark"}),
            ("📊 REPORTING", {"report", "export", "status", "conformance"}),
            ("🔍 TRUST", {"validate", "joint-validate", "parity", "repro"}),
        )
    )
    preset_count = sum(
        1 for s in b.api_symbols if s.startswith("create_") and s.endswith("_mlp")
    )
    native_count = sum(1 for s in b.api_symbols if s.startswith("native_"))
    api_chips = tuple(
        Chip(label=name, sub=sub, accent=COLORS["entry"], tooltip=sub)
        for name, sub in (
            ("SystemTrainer", ".fit() → history"),
            ("compose_joint_system", "6-axis composition"),
            ("create_task", "task factory"),
            ("create_*_mlp", f"{preset_count} 5-D presets"),
            ("native_*", f"{native_count} native models"),
            ("ExperimentConfig", "+ Model/Training/Data/Hardware"),
        )
    )
    demo_chips = tuple(
        Chip(
            label=d, sub=s.replace("Expected: ", ""), accent=COLORS["entry"], tooltip=s
        )
        for d, s in b.demos
    )
    return (
        GroupedChipsRow(
            f"⌨️ comp CLI — {len(b.cli)} subcommands, every one works end-to-end or does not exist",
            cli_groups,
        ),
        ChipsRow(
            f"🐍 Python API — {len(b.api_symbols)} public symbols (lazy __all__)",
            api_chips,
        ),
        ChipsRow(
            f"🎬 Demos & figures — {len(b.demos)} scripts · {len(b.gallery)} gallery demos",
            (
                *demo_chips,
                Chip(
                    label=f"docs/figures gallery ({len(b.gallery)})",
                    accent=COLORS["entry"],
                    tooltip=f"{len(b.gallery)} locked gallery demos",
                ),
            ),
        ),
    )


def _tasks_rows(b: Bundle) -> tuple[Row, ...]:
    task_chips = tuple(
        Chip(
            label=f"{DOMAIN_EMOJI.get(d, '📌')} {d}",
            sub=f"{len(b.tasks.get(DOMAIN_GROUP[d], ()))} tasks"
            if b.tasks.get(DOMAIN_GROUP[d])
            else "via create_task()",
            accent=COLORS["tasks"],
            tooltip=f"{d} domain · {len(b.tasks.get(DOMAIN_GROUP[d], ()))} tasks",
        )
        for d in b.domains
    )
    total_tasks = sum(len(v) for v in b.tasks.values())
    task_groups = tuple(
        Group(
            name=f"{DOMAIN_EMOJI.get(d, '📌')} {d}",
            chips=tuple(
                Chip(
                    label=n,
                    mono=True,
                    accent=COLORS["tasks"],
                    tooltip=n,
                )
                for n in b.tasks.get(DOMAIN_GROUP[d], ())
            ),
        )
        for d in b.domains
        if b.tasks.get(DOMAIN_GROUP[d])
    )
    return (
        TextRow(
            "🗺 create_task(name, device='cpu', quick_mode) → task.setup() → task.get_dataloader('train')"
        ),
        ChipsRow(f"🧩 {len(b.domains)} domains (domains registry)", task_chips),
        GroupedChipsRow(
            f"📋 SUPPORTED_TASKS ({total_tasks}) — offline-resolvable subset",
            task_groups,
        ),
    )


def _kernel_rows(b: Bundle) -> tuple[Row, ...]:
    stage_steps = tuple(
        FlowStep(
            label=s.label,
            sub=STAGE_SHORT.get(s.key, s.summary),
            color=COLORS["kernel"],
            tooltip=s.summary if s.summary else s.label,
        )
        for s in b.stages
    )
    policy_chips = tuple(
        Chip(
            label=p.key,
            sub=p.class_name,
            accent=COLORS["kernel"],
            tooltip=p.summary,
        )
        for p in b.policies
    )
    measured = [n for n, m in b.objectives if m]
    registry_summary = tuple(
        Chip(label=label, sub=sub, accent=COLORS["kernel"], tooltip=sub)
        for label, sub in (
            (
                "CAPABILITIES",
                f"{b.capabilities} conformance rows (C1–C{b.capabilities})",
            ),
            ("CONSTRAINTS", f"{b.constraints} legality constraints"),
            ("LEGALITY DSL", "expression engine — identical for every policy"),
            ("SearchSpace", "spec-derived, legality-filtered"),
            ("ContrastDesign", "OFAT / factorial DOE + DataOrigin"),
        )
    )
    return (
        FlowRow(
            f"▶ Pipeline S1–S{len(b.stages)} — PipelineRunner, registry-locked stages",
            stage_steps,
        ),
        ChipsRow(
            f"🧠 Policies — POLICY_CATALOG · {len(b.policies)} · interchangeable per round (U4)",
            policy_chips,
        ),
        Columns((
            TableRow(
                f"🎯 OBJECTIVES ({len(b.objectives)}) — {len(measured)} ✓ / {len(b.objectives) - len(measured)} 🔬",
                ("objective", "status"),
                tuple((o, "✓ measured" if m else "🔬 target") for o, m in b.objectives),
            ),
            TableRow(
                f"⚖️ PRIORS ({len(b.priors)})",
                ("prior",),
                tuple((pr,) for pr in b.priors),
            ),
            TableRow(
                f"🧾 RunSpec fields ({len(b.run_spec_fields)})",
                ("field",),
                tuple((f,) for f in b.run_spec_fields),
            ),
        )),
        ChipsRow("🧮 Registry counts & DSLs", registry_summary),
    )


def _system_rows(b: Bundle) -> tuple[Row, ...]:
    return (
        Section(
            "🏗 Composition",
            (
                FlowRow(
                    "🔗 compose_joint_system(substrate, geometry, dynamics, plasticity, credit, update)",
                    (
                        FlowStep(
                            label="compose",
                            sub="6 axis args",
                            color=COLORS["system"],
                            tooltip="bridge: 6 axis args → System",
                        ),
                        FlowStep(
                            label="SystemConfig.validate()",
                            sub="whitelist → compatible region",
                            color=COLORS["system"],
                            tooltip="whitelist: compatible combinations",
                        ),
                        FlowStep(
                            label="System",
                            sub="θ params + x state (settle contract)",
                            color=COLORS["system"],
                            tooltip="writable params θ + state x with settle contract",
                        ),
                    ),
                ),
                ChipsRow(
                    "🧰 5-D & helpers (P = NullPlasticity subspace)",
                    tuple(
                        Chip(label=n, accent=COLORS["system"], tooltip=n)
                        for n in (
                            "compose_system (5-D)",
                            "create_eqprop_mlp",
                            "extract_config",
                            "train_task / train_on_task",
                        )
                    ),
                ),
                TextRow(
                    "NullPlasticity ⇒ 5-D delegation path · P ≠ null ⇒ 6-D joint, ψ written back to θ"
                ),
            ),
        ),
        Section(
            "⚙️ Configuration",
            (
                TableRow(
                    f"⚙ SystemTrainerConfig ({len(b.configs['SystemTrainerConfig'])} fields)",
                    ("field",),
                    tuple((f,) for f in b.configs["SystemTrainerConfig"]),
                ),
            ),
        ),
    )


def _train_rows(b: Bundle) -> tuple[Row, ...]:
    loop_steps = tuple(
        FlowStep(
            label=label,
            sub=sub,
            color=color,
            tooltip=sub if sub else label,
        )
        for label, sub, color in (
            ("fit()", "per-epoch loop", COLORS["train"]),
            ("settle · D", "state → minimum / fixed point", AXIS_COLOR["dynamics"]),
            ("forward · G", "route activations", AXIS_COLOR["geometry"]),
            ("credit · C", "pseudo-gradient / error", AXIS_COLOR["credit"]),
            ("update · U", "consolidate Δθ", AXIS_COLOR["update"]),
        )
    )
    history_chips = tuple(
        Chip(label=m, accent=COLORS["train"], tooltip=m) for m in b.history_metrics
    )
    return (
        Section(
            "🔁 Epoch loop",
            (
                FlowRow(
                    "one epoch: settle → forward → credit → update (repeat until convergence)",
                    loop_steps,
                    loop_back=True,
                ),
                TextRow(
                    "evaluator adds walltime_s · param_count (MEASURED_METRICS) · "
                    "settle mutates state in place, credit reads post-settle state"
                ),
            ),
        ),
        Section(
            "📈 Telemetry",
            (
                ChipsRow(
                    f"history (per epoch, {len(b.history_metrics)} METRICS)",
                    history_chips,
                ),
            ),
        ),
    )


def _evidence_rows(b: Bundle) -> tuple[Row, ...]:
    store_chips = tuple(
        Chip(label=m, accent=COLORS["evidence"], tooltip=m) for m in b.store_methods[:8]
    )
    return (
        Section(
            "🗃 Store & schema",
            (
                ChipsRow(
                    f"RecordStore methods ({len(b.store_methods)}) — threading lock · atomic append",
                    store_chips,
                ),
                TableRow(
                    f"🧾 Record fields ({len(b.record_fields)}, schema v{b.schema_version} — fail-closed)",
                    ("field",),
                    tuple((f,) for f in b.record_fields),
                ),
            ),
        ),
        Section(
            "🏷 Discipline",
            (
                ChipsRow(
                    "Claim tiers & schema discipline",
                    tuple(
                        Chip(label=tier, accent=COLORS["evidence"], tooltip=tier)
                        for tier in (
                            "gate verdict · defect cause · maturity",
                            "measurement_key (deterministic)",
                            f"UnsupportedSchemaVersionError (v{b.schema_version} fail-closed)",
                            "unknown column survives bumps verbatim",
                        )
                    ),
                ),
            ),
        ),
    )


def _surface_rows(b: Bundle) -> tuple[Row, ...]:
    surface_cli = tuple(
        Chip(label=c, sub=s[:36], accent=COLORS["surface"], tooltip=s)
        for c, s in b.cli
        if c in {"report", "export", "conformance", "status", "run"}
    )
    claim_steps = tuple(
        FlowStep(label=lv, sub=tier, color=COLORS["surface"], tooltip=f"{lv} {tier}")
        for lv, tier in (
            ("L1", "analytical"),
            ("L2", "machine-checked"),
            ("L3", "certified-numerical"),
            ("L4", "sampled-numerical"),
            ("L5", "empirical"),
        )
    )
    package_chips = tuple(
        Chip(label=p, accent=COLORS["surface"], tooltip=p) for p in b.packages
    )
    return (
        Section(
            "🖥 Surface",
            (
                ChipsRow("comp report surface", surface_cli),
                FlowRow("Verification levels — claim-strength discipline", claim_steps),
            ),
        ),
        Section(
            "📦 Packages",
            (
                ChipsRow(
                    "CEEC + workspace packages",
                    (
                        *package_chips,
                        Chip(
                            label="CEEC epistemic governance",
                            sub="banned-overclaim audit · conformance C1–C88",
                            accent=COLORS["surface"],
                        ),
                    ),
                ),
            ),
        ),
    )


_ROW_BUILDERS: dict[str, Callable[[Bundle], tuple[Row, ...]]] = {
    "entry": _entry_rows,
    "tasks": _tasks_rows,
    "kernel": _kernel_rows,
    "ontology": lambda b: (AxesRow(_axis_boxes(b)),),
    "system": _system_rows,
    "train": _train_rows,
    "evidence": _evidence_rows,
    "surface": _surface_rows,
}

_TITLES: dict[str, str] = {
    "entry": "🚪 Entry Points",
    "tasks": "🎯 Tasks & Data",
    "kernel": "🧪 Experiment Kernel — question → governed evidence",
    "ontology": "🧬 6-Axis Ontology — System = Substrate × Geometry × StateDynamics × Plasticity × Credit × Update",
    "system": "🏗️ System & Composition",
    "train": "⚡ Training Loop — SystemTrainer.fit()",
    "evidence": "💾 Evidence Store — one DuckDB, single writer",
    "surface": "📊 Surface & Governance",
}


def build_panels(b: Bundle) -> tuple[Panel, ...]:
    return tuple(
        Panel(key=key, title=_TITLES[key], rows=_ROW_BUILDERS[key](b))
        for key in _TITLES
    )


# ---------------------------------------------------------------------------
# 4. Layout engine: content-driven sizing, band stacking, edge routing
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Style:
    """Every tunable metric in one place; geometry below is computed."""

    margin: float = 60.0
    header_h: float = 96.0
    footer_h: float = 56.0
    band_gap: float = 72.0
    panel_pad: float = 14.0
    title_h: float = 36.0
    row_gap: float = 8.0
    chip_gap: float = 8.0
    chip_v_gap: float = 6.0
    max_content_w: float = 1440.0
    flow_max_cols: int = 6
    step_gap: float = 14.0
    step_min_w: float = 104.0
    box_gap: float = 12.0
    chip_font: float = 11.0
    sub_font: float = 7.5
    mono_font: float = 9.0
    note_font: float = 8.5
    label_font: float = 12.5
    step_label_font: float = 12.5
    step_sub_font: float = 7.5
    edge_font: float = 9.0
    legend_font: float = 8.0
    group_header_font: float = 8.5
    axis_header_font: float = 12.0
    axis_cfg_font: float = 8.5
    axis_field_font: float = 7.5
    group_inset: float = 6.0
    legend_gap: float = 14.0
    legend_swatch: float = 11.0
    legend_dash_w: float = 22.0
    legend_axis_sq: float = 5.0
    legend_axis_gap: float = 2.5
    rail_label_offset: float = 18.0


STYLE = Style()

BANDS: tuple[tuple[str, ...], ...] = (
    ("entry",),
    ("tasks", "kernel"),
    ("ontology",),
    ("system", "train"),
    ("surface", "evidence"),
)

LEFT_RAIL: tuple[str, ...] = ("tasks", "system", "surface")
RIGHT_RAIL: tuple[str, ...] = ("kernel", "evidence")


@dataclass(frozen=True, slots=True)
class Pos:
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2.0

    @property
    def cy(self) -> float:
        return self.y + self.h / 2.0

    @property
    def bottom(self) -> float:
        return self.y + self.h


@dataclass(frozen=True, slots=True)
class Layout:
    pos: dict[str, Pos]
    canvas_w: float
    canvas_h: float
    band_gaps: tuple[tuple[float, float], ...]


def step_metrics(step: FlowStep) -> tuple[float, float]:
    label_w = text_w(step.label, STYLE.step_label_font) * 1.04
    sub_lines = _wrap_text(step.sub, STYLE.step_sub_font, 400.0)[:2] if step.sub else []
    sub_w = max((text_w(line, STYLE.step_sub_font) for line in sub_lines), default=0.0)
    w = max(STYLE.step_min_w, 18.0 + max(label_w, sub_w))
    h = 30.0 + 10.0 * min(len(sub_lines), 2)
    return w, h


def chip_positions(
    chips: tuple[Chip, ...], gap: float, w: float
) -> tuple[list[tuple[float, float]], float]:
    if not chips:
        return [], 0.0
    row_h = max(c.h for c in chips)
    positions: list[tuple[float, float]] = []
    x = y = 0.0
    for c in chips:
        if x > 0.0 and x + gap + c.w > w:
            x, y = 0.0, y + row_h + STYLE.chip_v_gap
        positions.append((x, y))
        x += c.w + gap
    rows = len({py for _, py in positions})
    return positions, (rows - 1) * (row_h + STYLE.chip_v_gap) + row_h


def flow_metrics(
    steps: tuple[FlowStep, ...], w: float
) -> tuple[int, int, float, float]:
    m = [step_metrics(s) for s in steps]
    sw = max(mw for mw, _ in m)
    sh = max(mh for _, mh in m)
    stride = sw + STYLE.step_gap
    cols = max(
        1, min(STYLE.flow_max_cols, len(steps), int((w + STYLE.step_gap) // stride))
    )
    rows = -(-len(steps) // cols)
    return cols, rows, sw, sh


def box_natural_w(box: AxisBox) -> float:
    chip_w = max((c.w for c in box.primitives), default=0.0)
    header_w = text_w(f"{AXIS_SYMBOL[box.axis]} · {box.axis}", STYLE.axis_header_font)
    fields = " · ".join(box.config_fields[:4])
    if len(box.config_fields) > 4:
        fields += f" · +{len(box.config_fields) - 4}"
    cfg_w = max(
        text_w(f"⚙ {box.config_name}", STYLE.axis_cfg_font),
        text_w(fields, STYLE.axis_field_font),
    )
    return 12.0 + max(chip_w, header_w, cfg_w) + 12.0


def _grouped_chips_preferred_w(row: GroupedChipsRow) -> float:
    row_label_w = text_w(row.label, STYLE.label_font)
    max_w = row_label_w
    for g in row.groups:
        if g.name:
            max_w = max(max_w, text_w(g.name, 9.5))
        if g.chips:
            one = sum(c.w for c in g.chips) + row.gap * (len(g.chips) - 1)
            max_w = max(max_w, min(one, STYLE.max_content_w))
    return min(max_w, STYLE.max_content_w)


def _table_col_w(
    rows: tuple[tuple[str, ...], ...], headers: tuple[str, ...], ci: int
) -> float:
    cells = [headers[ci], *(r[ci] for r in rows)]
    return max(text_w(c, STYLE.mono_font) for c in cells) + 14.0


def _table_preferred_w(row: TableRow) -> float:
    rows, headers = row.rows, row.headers
    half = (len(rows) + 1) // 2 if len(rows) > 12 else len(rows)
    lrows, rrows = rows[:half], rows[half:]

    def gw(rs: tuple[tuple[str, ...], ...]) -> float:
        if not rs and not headers:
            return 0.0
        src = rs if rs else (headers,)
        return sum(_table_col_w(src, headers, ci) for ci in range(len(headers)))

    gw_total = gw(lrows) + (gw(rrows) + 24.0 if rrows else 0.0)
    return min(max(text_w(row.label, STYLE.label_font), gw_total), STYLE.max_content_w)


def _pw_chips(row: ChipsRow) -> float:
    one = (
        sum(c.w for c in row.chips) + row.gap * (len(row.chips) - 1)
        if row.chips
        else 0.0
    )
    return min(max(text_w(row.label, STYLE.label_font), one), STYLE.max_content_w)


def _pw_flow(row: FlowRow) -> float:
    m = [step_metrics(st) for st in row.steps]
    sw = max(mw for mw, _ in m)
    cols = min(STYLE.flow_max_cols, len(row.steps))
    return min(cols * (sw + STYLE.step_gap) - STYLE.step_gap, STYLE.max_content_w)


def _pw_fields(row: FieldsRow) -> float:
    return min(
        text_w(row.text, STYLE.mono_font if row.mono else 10.0), STYLE.max_content_w
    )


def _pw_text(row: TextRow) -> float:
    return min(text_w(row.text, STYLE.note_font), STYLE.max_content_w)


def _pw_axes(row: AxesRow) -> float:
    return sum(box_natural_w(b) for b in row.boxes) + STYLE.box_gap * (
        len(row.boxes) - 1
    )


def _pw_section(row: Section) -> float:
    return max(
        text_w(row.label, STYLE.label_font),
        max((row_preferred_w(c) for c in row.rows), default=0.0),
    )


def _pw_columns(row: Columns) -> float:
    ws = [min(row_preferred_w(c), STYLE.max_content_w) for c in row.rows]
    return min(sum(ws) + row.gap * (len(row.rows) - 1), STYLE.max_content_w)


def _col_widths(row: Columns, w: float) -> list[float]:
    ws = [min(row_preferred_w(c), STYLE.max_content_w) for c in row.rows]
    total = sum(ws) + row.gap * (len(ws) - 1)
    if total > w and total > 0:
        scale = (w - row.gap * (len(ws) - 1)) / sum(ws)
        ws = [x * scale for x in ws]
    return ws


def _rh_columns(row: Columns, w: float) -> float:
    ws = _col_widths(row, w)
    return max((row_h(c, cw) for c, cw in zip(row.rows, ws, strict=True)), default=0.0)


_PREFERRED_W: dict[type, Callable[..., float]] = {
    ChipsRow: _pw_chips,
    FlowRow: _pw_flow,
    FieldsRow: _pw_fields,
    TextRow: _pw_text,
    AxesRow: _pw_axes,
    GroupedChipsRow: _grouped_chips_preferred_w,
    TableRow: _table_preferred_w,
    Section: _pw_section,
    Columns: _pw_columns,
}


def row_preferred_w(row: Row) -> float:
    return _PREFERRED_W[type(row)](row)


def _rh_chips(row: ChipsRow, w: float) -> float:
    _, h = chip_positions(row.chips, row.gap, w)
    return 18.0 + (6.0 if row.chips else 0.0) + h


def _rh_flow(row: FlowRow, w: float) -> float:
    _, rows, _, sh = flow_metrics(row.steps, w)
    return 18.0 + 6.0 + rows * (sh + 10.0) + (16.0 if row.loop_back else 0.0)


def _rh_fields(row: FieldsRow, w: float) -> float:
    lines = _wrap_text(row.text, STYLE.mono_font if row.mono else 10.0, w)
    return 18.0 + 4.0 + len(lines) * 13.0


def _rh_text(row: TextRow, w: float) -> float:
    return len(_wrap_text(row.text, STYLE.note_font, w)) * 12.0 + 4.0


def _rh_axes(row: AxesRow, w: float) -> float:
    return box_h(row.boxes)


def _rh_grouped(row: GroupedChipsRow, w: float) -> float:
    return grouped_chips_h(row.groups, w, row.gap)


def _rh_table(row: TableRow, w: float) -> float:
    half = (len(row.rows) + 1) // 2 if len(row.rows) > 12 else len(row.rows)
    return 18.0 + 4.0 + 13.0 + half * 12.0


def _rh_section(row: Section, w: float) -> float:
    inner = STYLE.row_gap * (len(row.rows) - 1) if row.rows else 0.0
    return 22.0 + 4.0 + sum(row_h(c, w - 12.0) for c in row.rows) + inner + 6.0


_ROW_H: dict[type, Callable[..., float]] = {
    ChipsRow: _rh_chips,
    FlowRow: _rh_flow,
    FieldsRow: _rh_fields,
    TextRow: _rh_text,
    AxesRow: _rh_axes,
    GroupedChipsRow: _rh_grouped,
    TableRow: _rh_table,
    Section: _rh_section,
    Columns: _rh_columns,
}


def row_h(row: Row, w: float) -> float:
    return _ROW_H[type(row)](row, w)


def box_h(boxes: tuple[AxisBox, ...]) -> float:
    chip_h = 23.0
    return max(
        30.0 + 6.0 + len(b.primitives) * (chip_h + 5.0) + 8.0 + 40.0 + 8.0
        for b in boxes
    )


def grouped_chips_h(groups: tuple[Group, ...], w: float, gap: float) -> float:
    """Total height of a GroupedChipsRow content above its baseline y."""
    ty = 22.0
    for i, g in enumerate(groups):
        name_h = 14.0 if g.name else 0.0
        _, h = chip_positions(g.chips, gap, w)
        ty += 2 * STYLE.group_inset + name_h + h
        if i < len(groups) - 1:
            ty += gap
    return ty


def panel_metrics(panel: Panel) -> tuple[float, float]:
    content_w = min(STYLE.max_content_w, max(row_preferred_w(r) for r in panel.rows))
    w = content_w + 2.0 * STYLE.panel_pad
    h = (
        STYLE.title_h
        + 2.0 * STYLE.panel_pad
        + sum(row_h(r, content_w) for r in panel.rows)
        + STYLE.row_gap * len(panel.rows)
    )
    return w, h


def layout(panels: dict[str, Panel]) -> Layout:
    metrics = {k: panel_metrics(p) for k, p in panels.items()}
    band_ws = [
        sum(metrics[k][0] for k in band) + STYLE.band_gap * (len(band) - 1)
        for band in BANDS
    ]
    canvas_w = 2.0 * STYLE.margin + max(band_ws)
    pos: dict[str, Pos] = {}
    y = STYLE.header_h
    band_tops: list[float] = []
    band_bottoms: list[float] = []
    for band, bw in zip(BANDS, band_ws, strict=True):
        x = (canvas_w - bw) / 2.0
        band_h = 0.0
        for key in band:
            pw, ph = metrics[key]
            pos[key] = Pos(x, y, pw, ph)
            band_h = max(band_h, ph)
            x += pw + STYLE.band_gap
        band_tops.append(y)
        band_bottoms.append(y + band_h)
        y += band_h + STYLE.band_gap
    canvas_h = y - STYLE.band_gap + STYLE.footer_h
    gaps = tuple((band_bottoms[i], band_tops[i + 1]) for i in range(len(band_tops) - 1))
    return Layout(pos=pos, canvas_w=canvas_w, canvas_h=canvas_h, band_gaps=gaps)


@dataclass(frozen=True, slots=True)
class Edge:
    src: str
    dst: str
    label: str
    dashed: bool = False
    route: str = "elbow"
    primary: bool = False


def build_edges() -> tuple[Edge, ...]:
    return (
        Edge("entry", "tasks", "create_task(name)", primary=True),
        Edge("entry", "kernel", "comp run profile · question_first()"),
        Edge("tasks", "kernel", "task → RunSpec.task", route="h-gap", primary=True),
        Edge(
            "entry",
            "system",
            "compose + fit — direct library path",
            route="margin-left",
        ),
        Edge("kernel", "ontology", "S5 compose", primary=True),
        Edge("ontology", "system", "6 axes → System", primary=True),
        Edge(
            "system", "train", "SystemTrainer(system, cfg)", route="h-gap", primary=True
        ),
        Edge("train", "evidence", "history · walltime_s · param_count", primary=True),
        Edge("kernel", "evidence", "S8 atomic append", route="margin-right"),
        Edge(
            "evidence",
            "surface",
            "claims · conformance · status",
            route="h-gap",
            primary=True,
        ),
        Edge(
            "surface",
            "entry",
            "🔁 evidence → next question",
            dashed=True,
            route="margin-left-up",
        ),
    )


def left_rail_x(ly: Layout, outer: bool) -> float:
    return min(ly.pos[k].x for k in LEFT_RAIL) - (34.0 if outer else 14.0)


def right_rail_x(ly: Layout) -> float:
    return max(ly.pos[k].x + ly.pos[k].w for k in RIGHT_RAIL) + 34.0


def edge_points(e: Edge, ly: Layout) -> list[tuple[float, float]]:
    s, d = ly.pos[e.src], ly.pos[e.dst]
    match e.route:
        case "margin-left":
            mx = left_rail_x(ly, True)
            return [
                (s.x, s.y + 46.0),
                (mx, s.y + 46.0),
                (mx, d.y - 26.0),
                (d.cx, d.y - 26.0),
                (d.cx, d.y),
            ]
        case "margin-left-up":
            mx = left_rail_x(ly, False)
            return [
                (s.x, s.cy),
                (mx, s.cy),
                (mx, d.y + 24.0),
                (d.x, d.y + 24.0),
            ]
        case "margin-right":
            rx = right_rail_x(ly)
            return [
                (s.x + s.w, s.y + 60.0),
                (rx, s.y + 60.0),
                (rx, d.cy),
                (d.x + d.w, d.cy),
            ]
        case "h-gap":
            return [
                (s.x + s.w if s.x < d.x else s.x, s.cy),
                (d.x if s.x < d.x else d.x + d.w, d.cy),
            ]
        case _:
            lane = _gap_y(ly, s.bottom, d.y)
            return [(s.cx, s.bottom), (s.cx, lane), (d.cx, lane), (d.cx, d.y)]


def _gap_at(ly: Layout, y1: float, y2: float) -> tuple[float, float]:
    """Band-gap containing the y1..y2 midpoint, else the nearest one."""
    mid = (min(y1, y2) + max(y1, y2)) / 2.0
    for top, bot in ly.band_gaps:
        if top <= mid <= bot:
            return (top, bot)
    return min(ly.band_gaps, key=lambda g: abs((g[0] + g[1]) / 2.0 - mid))


def _gap_y(ly: Layout, y1: float, y2: float) -> float:
    top, bot = _gap_at(ly, y1, y2)
    return (top + bot) / 2.0


def edge_label(e: Edge, ly: Layout) -> tuple[float, float, str]:
    pts = edge_points(e, ly)
    s = ly.pos[e.src]
    match e.route:
        case "margin-left":
            # outer rail: above the gap midpoint (inner-rail label sits below)
            return (
                left_rail_x(ly, True) + 8.0,
                _gap_y(ly, pts[1][1], pts[2][1]) - STYLE.rail_label_offset,
                "start",
            )
        case "margin-left-up":
            return (
                left_rail_x(ly, False) + 8.0,
                _gap_y(ly, pts[1][1], pts[2][1]) + STYLE.rail_label_offset,
                "start",
            )
        case "margin-right":
            return (right_rail_x(ly) - 8.0, _gap_y(ly, pts[1][1], pts[2][1]), "end")
        case "h-gap":
            return ((pts[0][0] + pts[1][0]) / 2.0, s.y - 24.0, "middle")
        case _:
            return ((pts[1][0] + pts[2][0]) / 2.0, pts[1][1] - 8.0, "middle")


def edge_label_placement(e: Edge, ly: Layout) -> tuple[float, float, float, float, str]:
    """Bounding box (x, y, w, h) and anchor of an edge's label, as rendered."""
    lx, ly_, anchor = edge_label(e, ly)
    w = text_w(e.label, STYLE.edge_font) + 12.0
    tx = lx - w + 4.0 if anchor == "end" else lx
    return (tx - 4.0, ly_ - 9.0, w, 15.0, anchor)


def _label_hits_panel(rx: float, ry: float, ew: float, eh: float, p: Pos) -> bool:
    return rx < p.x + p.w and rx + ew > p.x and ry < p.y + p.h and ry + eh > p.y


def _rects_overlap(
    a: tuple[float, float, float, float], b: tuple[float, float, float, float]
) -> bool:
    return (
        a[0] < b[0] + b[2]
        and a[0] + a[2] > b[0]
        and a[1] < b[1] + b[3]
        and a[1] + a[3] > b[1]
    )


def _verify_edge(e: Edge, ly: Layout) -> tuple[float, float, float, float]:
    """Raise if an edge or its label is out of bounds or overlaps a panel."""
    rx, ry, ew, eh, _ = edge_label_placement(e, ly)
    if not (
        rx >= -6
        and rx + ew <= ly.canvas_w + 6
        and ry >= -6
        and ry + eh <= ly.canvas_h + 6
    ):
        raise RuntimeError(f"edge-label {e.label!r} ({e.src}->{e.dst}) out of canvas")
    for key, p in ly.pos.items():
        if _label_hits_panel(rx, ry, ew, eh, p):
            raise RuntimeError(f"edge-label {e.label!r} overlaps panel {key}")
    for x, y in edge_points(e, ly):
        if not (-5 <= x <= ly.canvas_w + 5 and -5 <= y <= ly.canvas_h + 5):
            raise RuntimeError(f"edge {e.src}->{e.dst} out of bounds")
    if e.route != "h-gap":
        pts = edge_points(e, ly)
        ys = [y for _, y in pts]
        top, bot = _gap_at(ly, pts[1][1], pts[2][1])
        if top > max(ys) or bot < min(ys):
            raise RuntimeError(
                f"edge {e.src}->{e.dst} label gap does not intersect its rail span"
            )
    return (rx, ry, ew, eh)


def _verify_layout(ly: Layout) -> None:
    """Raise if any panel, edge, or edge-label is out of bounds or collides."""
    for key, p in ly.pos.items():
        if not (p.x >= 0 and p.x + p.w <= ly.canvas_w):
            raise RuntimeError(f"panel {key} out of canvas horizontally")
        if not (p.y > 0 and p.y + p.h < ly.canvas_h):
            raise RuntimeError(f"panel {key} out of canvas vertically")
    lx, ly0, lw, lh = _legend_block(ly.canvas_w)
    if lx < 0 or lx + lw > ly.canvas_w:
        raise RuntimeError("legend out of canvas horizontally")
    for key, p in ly.pos.items():
        if _label_hits_panel(lx, ly0, lw, lh, p):
            raise RuntimeError(f"legend overlaps panel {key}")
    rects = [(e, _verify_edge(e, ly)) for e in build_edges()]
    for i, (ea, ra) in enumerate(rects):
        for eb, rb in rects[i + 1 :]:
            if _rects_overlap(ra, rb):
                raise RuntimeError(
                    f"edge-label {ea.label!r} ({ea.src}->{ea.dst}) collides with "
                    f"edge-label {eb.label!r} ({eb.src}->{eb.dst})"
                )


# ---------------------------------------------------------------------------
# 5. SVG rendering
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return (
        s
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_text(
    x: float,
    y: float,
    s: str,
    size: float,
    fill: str,
    weight: str = "normal",
    anchor: str = "start",
    family: str = SANS,
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
        f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'
    )


def svg_rect(
    x: float,
    y: float,
    w: float,
    h: float,
    rx: float,
    fill: str,
    stroke: str | None = None,
    sw: float = 1.0,
    opacity: float = 1.0,
) -> str:
    s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if opacity != 1.0:
        s += f' fill-opacity="{opacity}"'
    return s + "/>"


def svg_poly(
    points: list[tuple[float, float]], color: str, sw: float, dashed: bool, marker: str
) -> str:
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{sw}"{dash} marker-end="url(#{marker})"/>'


def draw_chip(chip: Chip, x: float, y: float, color: str) -> str:
    accent = chip.accent or color
    if chip.enabled:
        parts = [
            svg_rect(x, y, chip.w, chip.h, 7.0, "white", accent, 1.2),
            f'<rect x="{x + 2.0:.1f}" y="{y + 4.0:.1f}" width="3.5" height="{chip.h - 8.0:.1f}" rx="1.5" fill="{accent}"/>',
        ]
    else:
        parts = [
            svg_rect(x, y, chip.w, chip.h, 7.0, "#f8fafc", accent, 1.0, opacity=0.5)
        ]
    ty = y + 15.0 if not chip.sub else y + 13.0
    fam = MONO if chip.mono else SANS
    parts.append(
        svg_text(
            x + 10.0,
            ty,
            chip.label + (" ✗" if not chip.enabled else ""),
            STYLE.chip_font if not chip.mono else STYLE.mono_font,
            "#1e293b",
            "600",
            family=fam,
        )
    )
    if chip.sub:
        parts.append(
            svg_text(
                x + 10.0,
                y + 26.0,
                _fit(chip.sub, STYLE.sub_font, chip.w - 14.0),
                STYLE.sub_font,
                "#64748b",
            )
        )
    rendered = "".join(parts)
    if chip.tooltip:
        return f"<g><title>{esc(chip.tooltip)}</title>{rendered}</g>"
    return rendered


def draw_flow_step(
    step: FlowStep, x: float, y: float, w: float, h: float, arrow_right: bool
) -> str:
    parts = [
        svg_rect(x, y, w, h, 9.0, "white", step.color, 1.4),
        svg_text(
            x + w / 2.0,
            y + 16.0,
            _fit(step.label, STYLE.step_label_font, w - 10.0),
            STYLE.step_label_font,
            "#1e293b",
            "700",
            anchor="middle",
        ),
    ]
    if step.sub:
        for i, line in enumerate(
            _wrap_text(step.sub, STYLE.step_sub_font, w - 12.0)[:2]
        ):
            parts.append(
                svg_text(
                    x + w / 2.0,
                    y + 28.0 + i * 10.0,
                    line,
                    STYLE.step_sub_font,
                    "#64748b",
                    anchor="middle",
                )
            )
    if arrow_right:
        parts.append(
            svg_poly(
                [(x + w + 1.5, y + h / 2.0), (x + w + 12.5, y + h / 2.0)],
                "#475569",
                1.5,
                False,
                "arr",
            )
        )
    rendered = "".join(parts)
    if step.tooltip:
        return f"<g><title>{esc(step.tooltip)}</title>{rendered}</g>"
    return rendered


_DRAW_ROW_HANDLERS: dict[type, Callable[..., tuple[str, float]]] = {}


def _draw_chips_row(
    row: ChipsRow, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    parts = [svg_text(x, y + 12, row.label, STYLE.label_font, "#475569", "700")]
    if not row.chips:
        return "".join(parts), 18.0
    positions, h = chip_positions(row.chips, row.gap, w)
    for (px, py), chip in zip(positions, row.chips, strict=True):
        parts.append(draw_chip(chip, x + px, y + 18 + py, color))
    return "".join(parts), 18.0 + 6.0 + h


def _draw_flow_row(
    row: FlowRow, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    parts = [svg_text(x, y + 12, row.label, STYLE.label_font, "#475569", "700")]
    cols, rows, sw, sh = flow_metrics(row.steps, w)
    stride = sw + STYLE.step_gap
    sy = y + 24
    for i, step in enumerate(row.steps):
        sx = x + (i % cols) * stride
        sy_i = sy + (i // cols) * (sh + 10.0)
        arrow = i + 1 < len(row.steps) and i % cols < cols - 1
        parts.append(draw_flow_step(step, sx, sy_i, sw, sh, arrow))
        if i + 1 < len(row.steps) and i % cols == cols - 1:
            cx = sx + sw / 2.0
            parts.append(
                svg_poly(
                    [(cx, sy_i + sh + 2.0), (cx, sy_i + sh + 8.0)],
                    "#475569",
                    1.5,
                    False,
                    "arr",
                )
            )
    if row.loop_back:
        last_col = (len(row.steps) - 1) % cols
        lx = x + last_col * stride + sw / 2.0
        by = sy + sh + 4.0
        parts.append(
            svg_poly(
                [(lx, sy + sh), (lx, by), (x + sw / 2.0, by), (x + sw / 2.0, sy + sh)],
                "#94a3b8",
                1.3,
                True,
                "arr",
            )
        )
        parts.append(
            svg_text(
                x + sw / 2.0 + 6.0,
                by + 11.0,
                "next step / until convergence",
                8.0,
                "#94a3b8",
            )
        )
    return "".join(parts), 18.0 + 6.0 + rows * (sh + 10.0) + (
        16.0 if row.loop_back else 0.0
    )


def _draw_fields_row(
    row: FieldsRow, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    fam = MONO if row.mono else SANS
    size = 9.5 if row.mono else 10.0
    parts = [svg_text(x, y + 12, row.label, STYLE.label_font, "#475569", "700")]
    ty = y + 24
    for line in _wrap_text(row.text, size, w):
        parts.append(svg_text(x, ty, line, size, "#334155", family=fam))
        ty += 13
    return "".join(parts), 18.0 + 4.0 + len(_wrap_text(row.text, size, w)) * 13.0


def _draw_text_row(
    row: TextRow, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    parts: list[str] = []
    ty = y + 4
    for line in _wrap_text(row.text, STYLE.note_font, w):
        parts.append(svg_text(x, ty, line, STYLE.note_font, "#64748b"))
        ty += 12
    return "".join(parts), len(_wrap_text(row.text, 9.5, w)) * 12.0 + 4.0


def _draw_axes_row(
    row: AxesRow, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    n = len(row.boxes)
    bw = min(box_natural_w(b) for b in row.boxes)
    bw = min(bw, (w - STYLE.box_gap * (n - 1)) / n) if n > 0 else 0.0
    parts: list[str] = []
    bx = x
    for box in row.boxes:
        parts.append(draw_axis_box(box, bx, y, bw))
        bx += bw + STYLE.box_gap
    return "".join(parts), row_h(row, w)


def _draw_grouped_chips_row(
    row: GroupedChipsRow, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    parts = [svg_text(x, y + 12, row.label, STYLE.label_font, "#475569", "700")]
    ty = y + 22.0
    gi = STYLE.group_inset
    pad = 3.0
    for i, g in enumerate(row.groups):
        name_h = 14.0 if g.name else 0.0
        positions, h = chip_positions(g.chips, row.gap, w)
        cluster_right = max(
            (px + c.w for (px, _), c in zip(positions, g.chips, strict=True)),
            default=0.0,
        )
        name_w = text_w(g.name, STYLE.group_header_font) if g.name else 0.0
        span = max(cluster_right, name_w)
        tint = g.accent or color
        parts.append(
            svg_rect(
                x - pad,
                ty,
                span + 2 * pad,
                gi + name_h + h + gi,
                8.0,
                tint + "14",
                tint + "40",
                0.8,
            )
        )
        if g.name:
            parts.append(
                svg_text(x, ty + gi + 6.0, g.name, STYLE.group_header_font, tint, "700")
            )
        ty += gi + name_h
        for (px, py), chip in zip(positions, g.chips, strict=True):
            parts.append(draw_chip(chip, x + px, ty + py, color))
        ty += h + gi
        if i < len(row.groups) - 1:
            ty += row.gap
    return "".join(parts), ty - y


def _draw_table_row(
    row: TableRow, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    parts = [svg_text(x, y + 12, row.label, STYLE.label_font, "#475569", "700")]
    half = (len(row.rows) + 1) // 2 if len(row.rows) > 12 else len(row.rows)
    grids = [row.rows[:half], row.rows[half:]]
    gx = x
    drawn = 0
    for gi, grid in enumerate(grids):
        if not grid:
            continue
        gy = y + 18.0
        col_ws = [_table_col_w(grid, row.headers, ci) for ci in range(len(row.headers))]
        for ci, h in enumerate(row.headers):
            parts.append(
                svg_text(
                    gx + sum(col_ws[:ci]),
                    gy + 9.0,
                    h.upper(),
                    STYLE.sub_font,
                    color,
                    "700",
                )
            )
        gy += 13.0
        for r in grid:
            for ci, cell in enumerate(r):
                fill = (
                    "#15803d"
                    if cell.startswith("✓")
                    else ("#b45309" if cell.startswith("🔬") else "#334155")
                )
                parts.append(
                    svg_text(
                        gx + sum(col_ws[:ci]),
                        gy + 9.0,
                        cell,
                        STYLE.mono_font,
                        fill,
                        family=MONO,
                    )
                )
            gy += 12.0
            drawn += 1
        gx += sum(col_ws) + 24.0
    return "".join(parts), 18.0 + 4.0 + 13.0 + half * 12.0


def _draw_section(
    row: Section, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    h = _rh_section(row, w)
    parts = [svg_rect(x, y, w, h, 8.0, color + "0d", color + "33", 0.8)]
    parts.append(
        svg_text(x + 8.0, y + 14.0, row.label, STYLE.group_header_font, color, "700")
    )
    cy = y + 22.0
    for c in row.rows:
        sub, ch = draw_row(c, x + 6.0, cy, color, w - 12.0)
        parts.append(sub)
        cy += ch + STYLE.row_gap
    return "".join(parts), h


def _draw_columns(
    row: Columns, x: float, y: float, color: str, w: float
) -> tuple[str, float]:
    parts: list[str] = []
    cx = x
    h = 0.0
    for c, cw in zip(row.rows, _col_widths(row, w), strict=True):
        sub, ch = draw_row(c, cx, y, color, cw)
        parts.append(sub)
        cx += cw + row.gap
        h = max(h, ch)
    return "".join(parts), h


_DRAW_ROW_HANDLERS = {
    ChipsRow: _draw_chips_row,
    TableRow: _draw_table_row,
    Section: _draw_section,
    Columns: _draw_columns,
    FlowRow: _draw_flow_row,
    FieldsRow: _draw_fields_row,
    TextRow: _draw_text_row,
    AxesRow: _draw_axes_row,
    GroupedChipsRow: _draw_grouped_chips_row,
}


def draw_row(row: Row, x: float, y: float, color: str, w: float) -> tuple[str, float]:
    handler = _DRAW_ROW_HANDLERS.get(type(row))
    if handler is None:
        raise TypeError(f"unknown row {row!r}")
    return handler(row, x, y, color, w)


def draw_axis_box(box: AxisBox, x: float, y: float, bw: float) -> str:
    color = AXIS_COLOR[box.axis]
    h = 30.0 + 6.0 + len(box.primitives) * (23.0 + 5.0) + 8.0 + 40.0 + 8.0
    parts = [svg_rect(x, y, bw, h, 10.0, color + "14", color, 1.3)]
    parts.append(
        svg_text(
            x + 8.0,
            y + 19.0,
            _fit(
                f"{AXIS_EMOJI[box.axis]} {AXIS_SYMBOL[box.axis]} · {box.axis}",
                STYLE.axis_header_font,
                bw - 16.0,
            ),
            STYLE.axis_header_font,
            color,
            "800",
        )
    )
    cy = y + 30
    for prim in box.primitives:
        parts.append(draw_chip(prim, x + 5.0, cy, color))
        cy += 23.0 + 5.0
    cfg_y = y + h - 48.0
    parts.append(svg_rect(x + 5.0, cfg_y, bw - 10.0, 40.0, 7.0, "white", color, 1.0))
    shown = " · ".join(box.config_fields[:4])
    if len(box.config_fields) > 4:
        shown += f" · +{len(box.config_fields) - 4}"
    parts.append(
        svg_text(
            x + 11.0,
            cfg_y + 14.0,
            _fit(
                f"⚙ {box.config_name} · {len(box.config_fields)} fields",
                STYLE.axis_cfg_font,
                bw - 22.0,
            ),
            STYLE.axis_cfg_font,
            "#1e293b",
            "700",
            family=MONO,
        )
    )
    parts.append(
        svg_text(
            x + 11.0,
            cfg_y + 28.0,
            _fit(shown, STYLE.axis_field_font, bw - 22.0),
            STYLE.axis_field_font,
            "#64748b",
            family=MONO,
        )
    )
    return "".join(parts)


def draw_panel(panel: Panel, p: Pos) -> str:
    color = panel.color
    content_w = p.w - 2.0 * STYLE.panel_pad
    parts = [
        svg_rect(p.x, p.y, p.w, p.h, 14.0, "white", color, 1.6),
        (
            f'<path d="M {p.x + 14.0:.1f} {p.y:.1f} h {p.w - 28.0:.1f} a 14 14 0 0 1 14 14 '
            f"v {STYLE.title_h - 14.0:.1f} h {-p.w:.1f} v {-(STYLE.title_h - 14.0):.1f} a 14 14 0 0 1 14 -14 z"
            f'" fill="{color}18"/>'
        ),
        svg_text(
            p.x + 16.0,
            p.y + 23.0,
            _fit(panel.title, 15.0, p.w - 40.0),
            13.5,
            color,
            "800",
        ),
    ]
    ry = p.y + STYLE.title_h + STYLE.panel_pad
    for row in panel.rows:
        content, drawn_h = draw_row(row, p.x + STYLE.panel_pad, ry, color, content_w)
        parts.append(content)
        ry += drawn_h + STYLE.row_gap
    return "".join(parts)


LEGEND: tuple[tuple[str, str, str], ...] = (
    ("panel", "entry", "entry"),
    ("panel", "tasks", "tasks & data"),
    ("panel", "kernel", "kernel"),
    ("panel", "ontology", "ontology"),
    ("panel", "system", "system"),
    ("panel", "train", "training"),
    ("panel", "evidence", "evidence"),
    ("panel", "surface", "surface"),
    ("dash", "", "dashed: evidence → next question"),
    ("axes", "", "axis colors S G D P C U"),
)


def _legend_metrics(kind: str) -> tuple[float, float]:
    """(swatch width, text x-offset from item origin) for a legend item kind."""
    match kind:
        case "dash":
            return STYLE.legend_dash_w, STYLE.legend_dash_w + 4.0
        case "axes":
            w = 6.0 * STYLE.legend_axis_sq + 5.0 * STYLE.legend_axis_gap
            return w, w + 4.0
        case _:
            return STYLE.legend_swatch, STYLE.legend_swatch + 4.0


def _legend_layout(canvas_w: float) -> tuple[float, list[float]]:
    """(x0, col_w) shared by render and verification."""
    totals = [
        _legend_metrics(kind)[1] + text_w(label, STYLE.legend_font)
        for kind, _, label in LEGEND
    ]
    n_cols = 5
    col_w = [
        max(totals[i], totals[i + n_cols] if i + n_cols < len(totals) else 0.0)
        for i in range(n_cols)
    ]
    x0 = canvas_w - STYLE.margin - sum(col_w) - (n_cols - 1) * STYLE.legend_gap
    return x0, col_w


def _legend_block(canvas_w: float) -> tuple[float, float, float, float]:
    """Bounding (x, y, w, h) of the whole legend block."""
    x0, col_w = _legend_layout(canvas_w)
    rows = (len(LEGEND) + 4) // 5
    top = 66.0 - 11.0
    return (x0, top, sum(col_w) + 4.0 * STYLE.legend_gap, rows * 15.0 + 2.0)


def render_legend(canvas_w: float) -> str:
    x0, col_w = _legend_layout(canvas_w)
    parts: list[str] = []
    for i, (kind, key, label) in enumerate(LEGEND):
        col = i % 5
        row_i = i // 5
        sx = x0 + sum(col_w[:col]) + col * STYLE.legend_gap
        sy = 66.0 + row_i * 15.0
        sw_w, text_dx = _legend_metrics(kind)
        match kind:
            case "dash":
                parts.append(
                    svg_poly(
                        [(sx, sy - 4.5), (sx + sw_w - 5.0, sy - 4.5)],
                        "#9333ea",
                        1.5,
                        True,
                        "arrp",
                    )
                )
            case "axes":
                for ax_i, ax in enumerate(tuple(AXIS_COLOR)):
                    parts.append(
                        svg_rect(
                            sx + ax_i * (STYLE.legend_axis_sq + STYLE.legend_axis_gap),
                            sy - 4.5,
                            STYLE.legend_axis_sq,
                            STYLE.legend_axis_sq,
                            1.0,
                            AXIS_COLOR[ax],
                        )
                    )
            case _:
                parts.append(
                    svg_rect(sx, sy - 9.0, STYLE.legend_swatch, 9.0, 2.0, COLORS[key])
                )
        parts.append(svg_text(sx + text_dx, sy, label, STYLE.legend_font, "#475569"))
    return "".join(parts)


def render_svg(panels: tuple[Panel, ...], ly: Layout, b: Bundle) -> str:
    pmap = {p.key: p for p in panels}
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{ly.canvas_w:.0f}" '
            f'height="{ly.canvas_h:.0f}" viewBox="0 0 {ly.canvas_w:.0f} {ly.canvas_h:.0f}" '
            f'shape-rendering="geometricPrecision" text-rendering="geometricPrecision" '
            f'font-family="{SANS}">'
        ),
        "<defs>",
        '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#475569"/></marker>',
        '<marker id="arrp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#9333ea"/></marker>',
        '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.07"/></filter>',
        "</defs>",
        svg_rect(0, 0, ly.canvas_w, ly.canvas_h, 0.0, "#ffffff"),
    ]
    parts.append(
        svg_text(
            STYLE.margin,
            34.0,
            "🌌 Computronium — Architecture Cheat Sheet",
            21.0,
            "#0f172a",
            "800",
        )
    )
    parts.append(
        svg_text(
            STYLE.margin,
            54.0,
            (
                f"directed graph: outer flow + nested insets · {sum(len(v) for v in b.axes.values())} ontology primitives · "
                f"{sum(len(v) for v in b.tasks.values())} tasks · {len(b.stages)} kernel stages · "
                f"generated {datetime.date.today().isoformat()} @ {b.commit}"
            ),
            10.0,
            "#64748b",
        )
    )
    parts.append(render_legend(ly.canvas_w))
    for e in build_edges():
        pts = edge_points(e, ly)
        color = "#9333ea" if e.dashed else ("#1e293b" if e.primary else "#94a3b8")
        parts.append(
            svg_poly(
                pts,
                color,
                1.8 if not e.dashed else 1.5,
                e.dashed,
                "arrp" if e.dashed else "arr",
            )
        )
    for key, p in ly.pos.items():
        parts.append(f'<g filter="url(#sh)">{draw_panel(pmap[key], p)}</g>')
    for e in build_edges():
        rx, ry, ew, eh, anchor = edge_label_placement(e, ly)
        parts.append(svg_rect(rx, ry, ew, eh, 4.0, "white", "#e2e8f0", 0.8))
        parts.append(
            svg_text(
                rx + 4.0,
                ry + 11.0,
                e.label,
                STYLE.edge_font,
                "#334155",
                "600",
                anchor=anchor,
            )
        )
    parts.append(
        svg_text(
            STYLE.margin,
            ly.canvas_h - 24.0,
            (
                "regenerate: uv run python docs/cheatsheet/cheatsheet_create.py · datafile: docs/cheatsheet/cheatsheet.txt · "
                "ontology reflected from experiment.schema.axis.AXES_REGISTRIES · kernel from execution.{stage,policy} registries"
            ),
            9.0,
            "#94a3b8",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# 6. Datafile rendering (docs/cheatsheet/cheatsheet.txt)
# ---------------------------------------------------------------------------


_TXT_RENDERERS: dict[str, Callable[[Bundle], list[str]]] = {}


def _txt_entry(b: Bundle) -> list[str]:
    out: list[str] = []
    out.append(f"  comp CLI ({len(b.cli)} commands):")
    for c, s in b.cli:
        out.append(f"    comp {c:<14s} {s}")
    out.append(
        f"  Python API: {len(b.api_symbols)} public symbols (computronium.__all__)"
    )
    out.append(f"    examples: {', '.join(b.api_symbols[:12])}, ...")
    out.append(
        f"  Demos: {len(b.demos)} scripts under scripts/demos/; gallery: {len(b.gallery)} demos"
    )
    for d, s in b.demos:
        out.append(f"    {d}: {s}")
    return out


def _txt_tasks(b: Bundle) -> list[str]:
    out: list[str] = [f"  domains ({len(b.domains)}): {', '.join(b.domains)}"]
    for domain in b.domains:
        names = b.tasks.get(DOMAIN_GROUP[domain], ())
        out.append(
            f"    {domain:12s} ({len(names):2d}): {', '.join(names) if names else 'via create_task() only'}"
        )
    return out


def _txt_kernel(b: Bundle) -> list[str]:
    out: list[str] = [f"  RunSpec fields: {', '.join(b.run_spec_fields)}"]
    out.append(f"  pipeline stages ({len(b.stages)}):")
    for s in b.stages:
        out.append(f"    {s.label:11s} {s.summary}")
    out.append(
        f"  policies ({len(b.policies)}): {', '.join(p.key for p in b.policies)}"
    )
    measured = [n for n, m in b.objectives if m]
    unmeasured = [n for n, m in b.objectives if not m]
    out.append(
        f"  objectives ({len(b.objectives)}): measured {len(measured)} -> {', '.join(measured)}"
    )
    out.append(
        f"                   research targets {len(unmeasured)} -> {', '.join(unmeasured)}"
    )
    out.append(f"  priors ({len(b.priors)}): {', '.join(b.priors[:8])}, ...")
    out.append(
        f"  registries: capabilities={b.capabilities} constraints={b.constraints} policies_registry={b.policies_registry}"
    )
    return out


def _txt_ontology(b: Bundle) -> list[str]:
    out: list[str] = []
    for axis, prims in b.axes.items():
        fields = b.configs[CONFIG_FOR_AXIS[axis]]
        out.append(f"  {axis} ({len(prims)} primitives) · config {', '.join(fields)}")
        for p in prims:
            flag = "" if p.available else f"  UNAVAILABLE: {p.reason}"
            out.append(f"    {p.name:26s} {p.description}{flag}")
    return out


def _txt_system(b: Bundle) -> list[str]:
    return [
        "  SystemConfig = SubstrateConfig × GeometryConfig × StateDynamicsConfig"
        " × PlasticityConfig × CreditAssignmentConfig × ParameterUpdateConfig",
        f"  SystemTrainerConfig: {', '.join(b.configs['SystemTrainerConfig'])}",
    ]


def _txt_train(b: Bundle) -> list[str]:
    return [
        f"  history per epoch: {', '.join(b.history_metrics)}",
        f"  evaluator adds: {', '.join(b.extra_metrics)}",
    ]


def _txt_evidence(b: Bundle) -> list[str]:
    return [
        f"  RecordStore methods: {', '.join(b.store_methods)}",
        f"  Record fields (schema v{b.schema_version}): {', '.join(b.record_fields)}",
        "  claim tiers: gate verdict · defect cause · maturity",
    ]


def _txt_surface(b: Bundle) -> list[str]:
    return [
        f"  verification levels: {', '.join(b.verification)}",
        f"  workspace packages: {', '.join(b.packages)}",
    ]


_TXT_RENDERERS = {
    "entry": _txt_entry,
    "tasks": _txt_tasks,
    "kernel": _txt_kernel,
    "ontology": _txt_ontology,
    "system": _txt_system,
    "train": _txt_train,
    "evidence": _txt_evidence,
    "surface": _txt_surface,
}


def render_txt(b: Bundle, panels: tuple[Panel, ...]) -> str:
    out: list[str] = []
    add = out.append
    add("=" * 78)
    add("COMPUTRONIUM ARCHITECTURE — CHEATSHEET DATAFILE")
    add(
        f"generated {datetime.date.today().isoformat()} @ commit {b.commit} by docs/cheatsheet/cheatsheet_create.py"
    )
    add("artifacts: docs/cheatsheet/cheatsheet.svg (directed graph) · this file (data)")
    add("=" * 78)
    add("")
    add("OUTER GRAPH (directed edges between panels)")
    add("-" * 78)
    for e in build_edges():
        style = "dashed " if e.dashed else ""
        add(f"  {e.src:9s} -{style}> {e.dst:9s}   {e.label}")
    add("")
    for panel in panels:
        add("=" * 78)
        add(f"PANEL {panel.key.upper()} — {panel.title}")
        add("=" * 78)
        render = _TXT_RENDERERS.get(panel.key)
        if render:
            out.extend(render(b))
        add("")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# 7. Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="validate output geometry after writing"
    )
    args = parser.parse_args(argv)

    b = collect()
    panels = build_panels(b)
    pmap = {p.key: p for p in panels}
    ly = layout(pmap)
    svg = render_svg(panels, ly, b)
    txt = render_txt(b, panels)

    OUT_SVG.write_text(svg, encoding="utf-8")
    OUT_TXT.write_text(txt, encoding="utf-8")

    def _row_chips(r: Row) -> int:
        if isinstance(r, (Section, Columns)):
            return sum(_row_chips(c) for c in r.rows)
        return (
            len(getattr(r, "chips", ()))
            + len(getattr(r, "steps", ()))
            + len(getattr(r, "boxes", ()))
            + sum(len(g.chips) for g in getattr(r, "groups", ()))
        )

    n_chips = sum(_row_chips(r) for p in panels for r in p.rows)
    n_prims = sum(len(v) for v in b.axes.values())
    print(
        f"wrote {OUT_SVG.relative_to(ROOT)} ({len(svg) // 1024} KiB, {ly.canvas_h:.0f}px tall × {ly.canvas_w:.0f}px wide)"
    )
    print(f"wrote {OUT_TXT.relative_to(ROOT)} ({len(txt) // 1024} KiB)")
    print(
        f"reflected: {n_prims} primitives · {len(b.cli)} cli · {len(b.stages)} stages · "
        f"{len(b.policies)} policies · ~{n_chips} inner chips"
    )

    if args.check:
        ET.fromstring(svg)  # ruff: ignore[suspicious-xml-element-tree-usage] — parses our own generated SVG
        _verify_layout(ly)
        print("check: svg parses, all panels/edges/labels within canvas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
