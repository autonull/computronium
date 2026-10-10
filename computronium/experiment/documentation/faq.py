"""FAQ/Troubleshooting — curated from CI/CD failures and user reports.

Provides a searchable FAQ categorized by axis and error type.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FAQEntry:
    """Single FAQ entry."""

    id: str
    category: str  # axis name or "general"
    error_type: str  # e.g., "import", "config", "runtime", "performance"
    question: str
    answer: str
    workaround: str | None = None
    related_docs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


# Built-in FAQ database
_BUILTIN_FAQ: list[FAQEntry] = [
    FAQEntry(
        id="FAQ-001",
        category="general",
        error_type="import",
        question="ModuleNotFoundError: No module named 'computronium'",
        answer="Ensure the package is installed in your environment. Run `uv sync --dev --all-extras` from the repository root.",
        workaround='If using a virtual environment, ensure it\'s activated and `uv run python -c "import computronium"` works.',
        related_docs=["docs/development/setup.md"],
        tags=["setup", "environment"],
    ),
    FAQEntry(
        id="FAQ-002",
        category="general",
        error_type="import",
        question="ImportError: cannot import name 'X' from 'computronium.ontology'",
        answer="The ontology module uses lazy imports for heavy dependencies. Ensure all required extras are installed: `uv sync --dev --all-extras`.",
        workaround="Try importing from the specific submodule: `from computronium.ontology.substrate import DigitalSubstrate`",
        related_docs=["docs/architecture/ontology.md"],
        tags=["import", "lazy-loading"],
    ),
    FAQEntry(
        id="FAQ-003",
        category="substrate",
        error_type="config",
        question="ValueError: Unknown substrate_type: 'mps'",
        answer="The substrate_type must be one of the registered types: digital, analog, memristive, neuromorphic, optical, quantum, sparse, ternary, complex, noisy, quantized. 'mps' is a device, not a substrate type.",
        workaround="Use `device='mps'` in SubstrateConfig.digital() instead.",
        related_docs=["docs/ontology/substrate.md"],
        tags=["substrate", "config", "device"],
    ),
    FAQEntry(
        id="FAQ-004",
        category="geometry",
        error_type="config",
        question="ValueError: Unknown topology_type: 'cnn'",
        answer="The topology_type must match a registered geometry backend. For CNN-like architectures, use 'feedforward' with appropriate hidden_dims, or 'tile' for tile-based topologies.",
        workaround="Check available topologies with `comp method-card list --axis geometry`",
        related_docs=["docs/ontology/geometry.md"],
        tags=["geometry", "config", "topology"],
    ),
    FAQEntry(
        id="FAQ-005",
        category="dynamics",
        error_type="config",
        question="ValueError: Unknown dynamics_type: 'equilibrium_prop'",
        answer="The dynamics_type must be one of: energy_minimization, predictive_settling, error_predictive_coding, spike_integration, instantaneous, diffusion, lazy, pc_alm. 'equilibrium_prop' maps to 'energy_minimization'.",
        workaround="Use `StateDynamicsConfig.energy_minimization()` for Equilibrium Propagation.",
        related_docs=["docs/ontology/dynamics.md"],
        tags=["dynamics", "config", "equilibrium-propagation"],
    ),
    FAQEntry(
        id="FAQ-006",
        category="dynamics",
        error_type="runtime",
        question="RuntimeError: CUDA out of memory during settling",
        answer="Settling dynamics (especially energy_minimization) can use significant GPU memory. Reduce max_steps, enable gradient_checkpointing, or use a smaller batch size.",
        workaround="Set `gradient_checkpointing=True` in StateDynamicsConfig or reduce `batch_limit` in RunSpec.",
        related_docs=["docs/ontology/dynamics.md", "docs/performance/memory.md"],
        tags=["dynamics", "memory", "gpu", "settling"],
    ),
    FAQEntry(
        id="FAQ-007",
        category="credit",
        error_type="config",
        question="ValueError: Unknown credit_type: 'ff'",
        answer="The credit_type must be one of the registered types: local_contrastive, thermodynamic_contrast, random_projections, local_goodness, lemma, pepita, pc_alm, temporal_trace, target_inversion, homeostatic, gradient, backprop. 'ff' is a local_objective, not a credit_type.",
        workaround="Use `CreditAssignmentConfig.local_contrastive(local_objective='ff')` for Forward-Forward style credit.",
        related_docs=["docs/ontology/credit.md"],
        tags=["credit", "config", "forward-forward"],
    ),
    FAQEntry(
        id="FAQ-008",
        category="credit",
        error_type="runtime",
        question="RuntimeError: Shape mismatch in credit computation",
        answer="Credit assignment requires label-augmented inputs for local_contrastive (last label_dim features = one-hot target). Ensure your data pipeline adds the label channel.",
        workaround="Check data loading code; the b4 probe `scripts/probes/w2_ema_rung.py` shows the expected input format.",
        related_docs=["docs/ontology/credit.md", "scripts/probes/w2_ema_rung.py"],
        tags=["credit", "data", "label-augmentation"],
    ),
    FAQEntry(
        id="FAQ-009",
        category="update",
        error_type="config",
        question="ValueError: Unknown update_type: 'adam'",
        answer="The update_type must be one of the registered types: euclidean, riemannian_orthogonal, muon, adam, local_adam, ortho_adam, unit_rms, spectral_constrained, role_split, mean_norm, elastic_consolidation.",
        workaround="Check available updates with `comp method-card list --axis update`",
        related_docs=["docs/ontology/update.md"],
        tags=["update", "config", "optimizer"],
    ),
    FAQEntry(
        id="FAQ-010",
        category="update",
        error_type="runtime",
        question="RuntimeError: SVD failed in RiemannianOrthogonalUpdate",
        answer="SVD can fail on degenerate matrices. This is often caused by zero-gradient parameters or numerical instability. The update falls back to Euclidean update for that step.",
        workaround="Ensure gradients are non-zero; check for dead neurons. Set `ortho_steps > 0` to use Newton-Schulz iteration instead of exact SVD.",
        related_docs=["docs/ontology/update.md"],
        tags=["update", "svd", "muon", "numerical-stability"],
    ),
    FAQEntry(
        id="FAQ-011",
        category="plasticity",
        error_type="config",
        question="TypeError: PlasticityConfig is not a valid plasticity primitive",
        answer="PlasticityConfig is a configuration dataclass, not a primitive. Use one of the concrete plasticity classes: NullPlasticity, FastWeightPlasticity, RoutingPlasticity, RuleStatePlasticity, SubstrateCoupledPlasticity, TemporalPsiPlasticity, ConflictAdaptivePsiPlasticity, ClosedFormRidgePlasticity.",
        workaround="Import from `computronium.ontology.plasticity` or `computronium.core.plasticity.*`",
        related_docs=["docs/ontology/plasticity.md"],
        tags=["plasticity", "config", "import"],
    ),
    FAQEntry(
        id="FAQ-012",
        category="general",
        error_type="runtime",
        question="comp run fails with 'No runs found in store'",
        answer="The store database may be empty or at a different path. Ensure `--store` points to the correct DuckDB file.",
        workaround="Run `comp status --store path/to/store.duckdb` to verify the store exists and has runs.",
        related_docs=["docs/cli/store.md"],
        tags=["cli", "store", "database"],
    ),
    FAQEntry(
        id="FAQ-013",
        category="general",
        error_type="performance",
        question="Training is extremely slow on CPU",
        answer="Ensure you're using GPU acceleration. Set `device='cuda'` in SubstrateConfig or RunSpec. For multi-GPU, use `comp dashboard` with DDP backend.",
        workaround='Run `uv run python -c "import torch; print(torch.cuda.is_available())"` to verify CUDA is available.',
        related_docs=["docs/performance/gpu.md"],
        tags=["performance", "gpu", "cpu"],
    ),
    FAQEntry(
        id="FAQ-014",
        category="general",
        error_type="runtime",
        question="comp quality check-report fails with 'Missing required section'",
        answer="The report template requires specific sections: Abstract, Hypotheses, Methods, Results, Discussion, Limitations, Reproducibility. Ensure your report context includes all required fields.",
        workaround="Use `comp report --store ... --run-id ...` to generate a complete report first, then run quality check.",
        related_docs=["docs/quality-gates.md"],
        tags=["quality", "report", "sections"],
    ),
    FAQEntry(
        id="FAQ-015",
        category="general",
        error_type="config",
        question="How to run a multi-axis campaign?",
        answer="Use `comp campaign` with a YAML file declaring the axis combinations. See `examples/campaigns/` for templates.",
        workaround="Start with a single-axis sweep using `comp run` before composing into campaigns.",
        related_docs=["docs/campaigns.md", "examples/campaigns/"],
        tags=["campaign", "multi-axis", "yaml"],
    ),
    FAQEntry(
        id="FAQ-016",
        category="dynamics",
        error_type="runtime",
        question="Settling does not converge (convergence_threshold not met)",
        answer="Increase max_steps, increase step_size, or adjust convergence_threshold. Some dynamics (e.g., energy_minimization) require more steps for complex geometries.",
        workaround="Try `max_steps=100, step_size=0.2` for difficult configurations. Enable `track_free_energy_per_iter=True` to diagnose.",
        related_docs=["docs/ontology/dynamics.md"],
        tags=["dynamics", "convergence", "settling"],
    ),
    FAQEntry(
        id="FAQ-017",
        category="general",
        error_type="import",
        question="ImportError: cannot import name '_SETTLE_KERNEL' from 'computronium.ontology._settle_kernel'",
        answer="The compiled settle kernel requires Triton. Install with `uv add triton` or ensure Triton is available for your CUDA version.",
        workaround="The pure-Python fallback will be used automatically if Triton is unavailable (slower but functional).",
        related_docs=["docs/installation.md"],
        tags=["triton", "compile", "settle-kernel"],
    ),
    FAQEntry(
        id="FAQ-018",
        category="geometry",
        error_type="runtime",
        question="RuntimeError: TileGeometry requires block_act_count attribute",
        answer="TileGeometry expects a tile-block geometry with assembled blocks. Ensure the geometry was created via `geometry_from_config` with topology_type='tile'.",
        workaround="Use `GeometryConfig.tile(...)` to create the config, then `geometry_from_config(config)`.",
        related_docs=["docs/ontology/geometry.md"],
        tags=["geometry", "tile", "blocks"],
    ),
    FAQEntry(
        id="FAQ-019",
        category="general",
        error_type="runtime",
        question="comp hypothesis-campaign runs but produces no hypotheses",
        answer="The hypothesis templates require specific data in the store. Ensure you have runs with PASS records and sufficient axis coverage.",
        workaround="Run `comp catalog list --store ...` to verify store contents before running hypothesis campaigns.",
        related_docs=["docs/hypothesis-campaigns.md"],
        tags=["hypothesis", "campaign", "store"],
    ),
    FAQEntry(
        id="FAQ-020",
        category="general",
        error_type="config",
        question="How to enable deterministic runs for reproducibility?",
        answer="Set `deterministic=True` in RunSpec and `num_workers=0`. Also set `torch.use_deterministic_algorithms(True)` in your entry script.",
        workaround="Use the `quick-verify` profile which enables determinism by default.",
        related_docs=["docs/reproducibility.md"],
        tags=["reproducibility", "deterministic", "seed"],
    ),
]


def generate_faq(
    additional_entries: list[FAQEntry] | None = None,
) -> list[FAQEntry]:
    """Generate the complete FAQ list.

    Args:
        additional_entries: Optional additional FAQ entries to include.

    Returns:
        Complete list of FAQ entries.
    """
    faq = list(_BUILTIN_FAQ)
    if additional_entries:
        faq.extend(additional_entries)
    return faq


def export_faq(faq: list[FAQEntry], output_path: Path, format: str = "json") -> None:
    """Export FAQ to file.

    Args:
        faq: List of FAQ entries.
        output_path: Output file path.
        format: Export format (json, markdown).
    """
    if format == "json":
        data = [
            {
                "id": e.id,
                "category": e.category,
                "error_type": e.error_type,
                "question": e.question,
                "answer": e.answer,
                "workaround": e.workaround,
                "related_docs": e.related_docs,
                "tags": e.tags,
            }
            for e in faq
        ]
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif format == "markdown":
        lines = ["# FAQ / Troubleshooting\n"]
        lines.append(f"Generated: {len(faq)} entries\n")

        # Group by category
        by_category: dict[str, list[FAQEntry]] = {}
        for entry in faq:
            by_category.setdefault(entry.category, []).append(entry)

        for category in sorted(by_category.keys()):
            lines.append(f"## {category.capitalize()}\n")
            for entry in by_category[category]:
                lines.append(f"### {entry.id}: {entry.question}")
                lines.append(f"**Error Type**: {entry.error_type}")
                lines.append("")
                lines.append(entry.answer)
                if entry.workaround:
                    lines.append("")
                    lines.append(f"**Workaround**: {entry.workaround}")
                if entry.related_docs:
                    lines.append("")
                    lines.append("**Related Documentation**:")
                    for doc in entry.related_docs:
                        lines.append(f"- {doc}")
                if entry.tags:
                    lines.append("")
                    lines.append(f"**Tags**: {', '.join(entry.tags)}")
                lines.append("")
                lines.append("---")
                lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        raise ValueError(f"Unknown format: {format}")


def _build_faq_parser() -> argparse.ArgumentParser:
    """Build the FAQ CLI parser."""
    parser = argparse.ArgumentParser(
        prog="comp faq",
        description="FAQ / Troubleshooting — searchable knowledge base",
    )
    sub = parser.add_subparsers(dest="faq_command", metavar="<command>", required=True)

    # list command
    list_parser = sub.add_parser("list", help="List all FAQ entries")
    list_parser.add_argument(
        "--category", help="Filter by category (axis name or 'general')"
    )
    list_parser.add_argument("--error-type", help="Filter by error type")
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    # search command
    search_parser = sub.add_parser("search", help="Search FAQ entries")
    search_parser.add_argument(
        "query", help="Search query (matches question/answer/tags)"
    )
    search_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    # show command
    show_parser = sub.add_parser("show", help="Show a specific FAQ entry")
    show_parser.add_argument("id", help="FAQ ID (e.g., FAQ-001)")
    show_parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format",
    )

    # generate command
    generate_parser = sub.add_parser("generate", help="Generate FAQ to file")
    generate_parser.add_argument("--output", required=True, help="Output file")
    generate_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format",
    )

    return parser


def _print_faq_text(entries: list[FAQEntry]) -> None:
    """Print FAQ entries in text format."""
    if not entries:
        print("No FAQ entries found.")
        return

    for entry in entries:
        print(f"{entry.id} [{entry.category}/{entry.error_type}]")
        print(f"  Q: {entry.question}")
        print(f"  A: {entry.answer}")
        if entry.workaround:
            print(f"  Workaround: {entry.workaround}")
        if entry.tags:
            print(f"  Tags: {', '.join(entry.tags)}")
        print()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for FAQ commands."""
    parser = _build_faq_parser()
    args = parser.parse_args(argv)

    faq = generate_faq()

    if args.faq_command == "list":
        filtered = faq
        if args.category:
            filtered = [e for e in filtered if e.category == args.category]
        if args.error_type:
            filtered = [e for e in filtered if e.error_type == args.error_type]
        if args.tag:
            filtered = [e for e in filtered if args.tag in e.tags]

        if args.format == "text":
            _print_faq_text(filtered)
            print(f"Total: {len(filtered)} entries")
        elif args.format == "json":
            data = [
                {
                    "id": e.id,
                    "category": e.category,
                    "error_type": e.error_type,
                    "question": e.question,
                    "answer": e.answer,
                    "workaround": e.workaround,
                    "related_docs": e.related_docs,
                    "tags": e.tags,
                }
                for e in filtered
            ]
            print(json.dumps(data, indent=2))

    elif args.faq_command == "search":
        query = args.query.lower()
        filtered = [
            e
            for e in faq
            if query in e.question.lower()
            or query in e.answer.lower()
            or any(query in tag.lower() for tag in e.tags)
        ]

        if args.format == "text":
            _print_faq_text(filtered)
            print(f"Found: {len(filtered)} entries")
        elif args.format == "json":
            data = [
                {
                    "id": e.id,
                    "category": e.category,
                    "error_type": e.error_type,
                    "question": e.question,
                    "answer": e.answer,
                    "workaround": e.workaround,
                    "related_docs": e.related_docs,
                    "tags": e.tags,
                }
                for e in filtered
            ]
            print(json.dumps(data, indent=2))

    elif args.faq_command == "show":
        entry = next((e for e in faq if e.id == args.id), None)
        if not entry:
            print(f"FAQ entry not found: {args.id}", file=sys.stderr)
            return 1

        if args.format == "text":
            _print_faq_text([entry])
        elif args.format == "json":
            data = {
                "id": entry.id,
                "category": entry.category,
                "error_type": entry.error_type,
                "question": entry.question,
                "answer": entry.answer,
                "workaround": entry.workaround,
                "related_docs": entry.related_docs,
                "tags": entry.tags,
            }
            print(json.dumps(data, indent=2))
        elif args.format == "markdown":
            export_faq([entry], Path("/dev/stdout"), "markdown")

    elif args.faq_command == "generate":
        export_faq(faq, Path(args.output), args.format)
        print(f"Generated {len(faq)} FAQ entries to {args.output}")

    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
