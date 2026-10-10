"""Method Cards — auto-generated documentation for all ontology primitives.

Generates structured documentation for each primitive across all 6 axes:
substrate, geometry, dynamics, plasticity, credit, update.
"""

from __future__ import annotations

import argparse
import inspect
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class MethodCard:
    """Method card for a single ontology primitive."""

    axis: str
    name: str
    class_name: str
    module: str
    purpose: str
    config_options: dict[str, Any]
    limitations: list[str]
    examples: list[str]
    references: list[str] = field(default_factory=list)
    source_file: str | None = None
    source_lines: tuple[int, int] | None = None


def _get_axis_registries() -> dict[str, dict[str, type]]:
    """Get all axis registries from the ontology."""
    from computronium.ontology.dynamics._registry import DYNAMICS_REGISTRY
    from computronium.ontology.geometry import _GEOMETRY_BACKENDS
    from computronium.ontology.update import _UPDATE_BACKENDS

    # For substrate, use the concrete classes directly
    substrate_registry = {
        "digital": __import__(
            "computronium.ontology.substrate", fromlist=["DigitalSubstrate"]
        ).DigitalSubstrate,
        "analog": __import__(
            "computronium.ontology.substrate", fromlist=["AnalogSubstrate"]
        ).AnalogSubstrate,
        "memristive": __import__(
            "computronium.ontology.substrate", fromlist=["MemristiveSubstrate"]
        ).MemristiveSubstrate,
        "neuromorphic": __import__(
            "computronium.ontology.substrate", fromlist=["NeuromorphicSubstrate"]
        ).NeuromorphicSubstrate,
        "optical": __import__(
            "computronium.ontology.substrate", fromlist=["OpticalSubstrate"]
        ).OpticalSubstrate,
        "quantum": __import__(
            "computronium.ontology.substrate", fromlist=["QuantumSubstrate"]
        ).QuantumSubstrate,
        "sparse": __import__(
            "computronium.ontology.substrate", fromlist=["SparseSubstrate"]
        ).SparseSubstrate,
        "ternary": __import__(
            "computronium.ontology.substrate", fromlist=["TernarySubstrate"]
        ).TernarySubstrate,
        "complex": __import__(
            "computronium.ontology.substrate", fromlist=["ComplexSubstrate"]
        ).ComplexSubstrate,
        "noisy": __import__(
            "computronium.ontology.substrate", fromlist=["NoisySubstrate"]
        ).NoisySubstrate,
        "quantized": __import__(
            "computronium.ontology.substrate", fromlist=["QuantizedSubstrate"]
        ).QuantizedSubstrate,
    }

    # For credit, use the concrete classes directly
    credit_registry = {
        "local_contrastive": __import__(
            "computronium.ontology.credit", fromlist=["LocalContrastiveCredit"]
        ).LocalContrastiveCredit,
        "thermodynamic_contrast": __import__(
            "computronium.ontology.credit", fromlist=["ThermodynamicContrast"]
        ).ThermodynamicContrast,
        "random_projections": __import__(
            "computronium.ontology.credit", fromlist=["RandomProjectionsCredit"]
        ).RandomProjectionsCredit,
        "local_goodness": __import__(
            "computronium.ontology.credit", fromlist=["LocalGoodnessCredit"]
        ).LocalGoodnessCredit,
        "lemma": __import__(
            "computronium.ontology.credit", fromlist=["LemmaCredit"]
        ).LemmaCredit,
        "pepita": __import__(
            "computronium.ontology.credit", fromlist=["PepitaCredit"]
        ).PepitaCredit,
        "pc_alm": __import__(
            "computronium.ontology.credit", fromlist=["PCALMCredit"]
        ).PCALMCredit,
        "temporal_trace": __import__(
            "computronium.ontology.credit", fromlist=["TemporalTraceCredit"]
        ).TemporalTraceCredit,
        "target_inversion": __import__(
            "computronium.ontology.credit", fromlist=["TargetInversionCredit"]
        ).TargetInversionCredit,
        "homeostatic": __import__(
            "computronium.ontology.credit", fromlist=["HomeostaticCredit"]
        ).HomeostaticCredit,
        "gradient": __import__(
            "computronium.ontology.credit", fromlist=["GradientCredit"]
        ).GradientCredit,
        "backprop": __import__(
            "computronium.ontology.credit", fromlist=["BackpropCredit"]
        ).BackpropCredit,
    }

    # For plasticity, use the exported classes
    plasticity_registry = {
        "null": getattr(
            __import__("computronium.state", fromlist=[""]), "NullPlasticity", None
        ),
        "fast_weight": getattr(
            __import__("computronium.core.plasticity.fast_weights", fromlist=[""]),
            "FastWeightPlasticity",
            None,
        ),
        "routing": getattr(
            __import__("computronium.core.plasticity.routing", fromlist=[""]),
            "RoutingPlasticity",
            None,
        ),
        "rule_state": getattr(
            __import__("computronium.core.plasticity.rule_state", fromlist=[""]),
            "RuleStatePlasticity",
            None,
        ),
        "substrate_coupled": getattr(
            __import__("computronium.core.plasticity.substrate_coupled", fromlist=[""]),
            "SubstrateCoupledPlasticity",
            None,
        ),
        "temporal_psi": getattr(
            __import__("computronium.core.plasticity.temporal_psi", fromlist=[""]),
            "TemporalPsiPlasticity",
            None,
        ),
        "conflict_adaptive_psi": getattr(
            __import__("computronium.core.plasticity.adaptive_psi", fromlist=[""]),
            "ConflictAdaptivePsiPlasticity",
            None,
        ),
        "closed_form_ridge": getattr(
            __import__("computronium.core.plasticity.closed_form", fromlist=[""]),
            "ClosedFormRidgePlasticity",
            None,
        ),
    }
    plasticity_registry = {
        k: v for k, v in plasticity_registry.items() if v is not None
    }

    return {
        "substrate": substrate_registry,
        "geometry": {k: v.cls for k, v in _GEOMETRY_BACKENDS.items()},
        "dynamics": DYNAMICS_REGISTRY,
        "plasticity": plasticity_registry,
        "credit": credit_registry,
        "update": dict(_UPDATE_BACKENDS),
    }


def _extract_docstring_sections(docstring: str | None) -> dict[str, Any]:
    """Extract structured sections from a docstring."""
    if not docstring:
        return {"purpose": "", "config_options": {}, "limitations": [], "examples": []}

    sections: dict[str, Any] = {
        "purpose": "",
        "config_options": {},
        "limitations": [],
        "examples": [],
    }

    lines = docstring.strip().split("\n")
    current_section = "purpose"
    current_content: list[str] = []

    def _save_section(sec: str, content: list[str]) -> None:
        if sec == "purpose":
            sections["purpose"] = "\n".join(content).strip()
        elif sec == "limitations":
            sections["limitations"] = [
                line.strip("- ") for line in content if line.strip()
            ]
        elif sec == "examples":
            sections["examples"] = [
                line.strip("- ") for line in content if line.strip()
            ]

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            _save_section(current_section, current_content)

            section_name = stripped[3:].strip().lower()
            if "limitation" in section_name:
                current_section = "limitations"
            elif "example" in section_name:
                current_section = "examples"
            else:
                current_section = "purpose"
            current_content = []
        else:
            current_content.append(line)

    _save_section(current_section, current_content)

    return sections


def _extract_config_from_method(method: Any) -> dict[str, Any]:
    """Extract config options from a classmethod."""
    config_options = {}
    try:
        sig = inspect.signature(method)
        for param_name, param in sig.parameters.items():
            if param_name not in {"cls", "self"}:
                config_options[param_name] = {
                    "type": str(param.annotation)
                    if param.annotation != inspect.Parameter.empty
                    else "Any",
                    "default": param.default
                    if param.default != inspect.Parameter.empty
                    else None,
                    "description": "",
                }
    except ValueError, TypeError:
        pass
    return config_options


def _get_config_classmethod(cls: type) -> dict[str, Any]:
    """Extract config options from a primitive's config classmethod."""
    config_options = {}

    # Look for a classmethod that creates a config
    for name in {"config", "from_config", "create_config", "default_config"}:
        if hasattr(cls, name):
            method = getattr(cls, name)
            if callable(method):
                config_options.update(_extract_config_from_method(method))

    # Also check for Config inner class
    if hasattr(cls, "Config"):
        config_cls = getattr(cls, "Config")
        if inspect.isclass(config_cls):
            for field_name, field_info in getattr(
                config_cls, "__dataclass_fields__", {}
            ).items():
                config_options[field_name] = {
                    "type": str(field_info.type),
                    "default": field_info.default
                    if field_info.default is not field_info.default_factory
                    else None,
                    "description": "",
                }

    return config_options


def _get_source_location(cls: type) -> tuple[str | None, tuple[int, int] | None]:
    """Get source file and line numbers for a class."""
    try:
        source_file = inspect.getfile(cls)
        lines = inspect.getsourcelines(cls)
        return source_file, (lines[1], lines[1] + len(lines[0]) - 1)
    except OSError, TypeError:
        return None, None


def generate_method_cards(
    axis: str | None = None,
    include_internal: bool = False,
) -> list[MethodCard]:
    """Generate method cards for all ontology primitives.

    Args:
        axis: Optional axis to filter (substrate, geometry, dynamics, plasticity, credit, update).
        include_internal: Whether to include internal (_-prefixed) primitives.

    Returns:
        List of MethodCard objects.
    """
    registries = _get_axis_registries()

    if axis:
        if axis not in registries:
            raise ValueError(
                f"Unknown axis: {axis}. Available: {list(registries.keys())}"
            )
        registries = {axis: registries[axis]}

    cards = []

    for axis_name, registry in registries.items():
        for name, cls in registry.items():
            if cls is None:
                continue
            if not include_internal and name.startswith("_"):
                continue

            doc_sections = _extract_docstring_sections(cls.__doc__)
            config_options = _get_config_classmethod(cls)
            source_file, source_lines = _get_source_location(cls)

            card = MethodCard(
                axis=axis_name,
                name=name,
                class_name=cls.__name__,
                module=cls.__module__,
                purpose=doc_sections["purpose"]
                or f"{cls.__name__} primitive for {axis_name} axis",
                config_options=config_options,
                limitations=doc_sections["limitations"],
                examples=doc_sections["examples"],
                source_file=source_file,
                source_lines=source_lines,
            )
            cards.append(card)

    return cards


def export_method_cards(
    cards: list[MethodCard], output_path: Path, format: str = "json"
) -> None:
    """Export method cards to file.

    Args:
        cards: List of method cards.
        output_path: Output file path.
        format: Export format (json, markdown).
    """
    if format == "json":
        data = [
            {
                "axis": c.axis,
                "name": c.name,
                "class_name": c.class_name,
                "module": c.module,
                "purpose": c.purpose,
                "config_options": c.config_options,
                "limitations": c.limitations,
                "examples": c.examples,
                "references": c.references,
                "source_file": c.source_file,
                "source_lines": c.source_lines,
            }
            for c in cards
        ]
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif format == "markdown":
        _export_method_cards_markdown(cards, output_path)
    else:
        raise ValueError(f"Unknown format: {format}")


def _export_method_cards_markdown(cards: list[MethodCard], output_path: Path) -> None:
    """Export method cards as markdown."""
    lines = ["# Method Cards\n"]
    lines.append(f"Generated: {len(cards)} method cards\n")

    for card in cards:
        lines.append(f"## {card.axis.capitalize()}: {card.name}")
        lines.append(f"**Class**: `{card.class_name}` (`{card.module}`)")
        if card.source_file and card.source_lines:
            lines.append(
                f"**Source**: `{card.source_file}:{card.source_lines[0]}-{card.source_lines[1]}`"
            )
        lines.append("")
        lines.append("### Purpose")
        lines.append(card.purpose or "No description available.")
        lines.append("")

        if card.config_options:
            lines.append("### Configuration Options")
            lines.append("")
            lines.append("| Parameter | Type | Default | Description |")
            lines.append("|-----------|------|---------|-------------|")
            for param, info in card.config_options.items():
                lines.append(
                    f"| {param} | {info.get('type', 'Any')} | "
                    f"{info.get('default', 'required')} | {info.get('description', '')} |"
                )
            lines.append("")

        if card.limitations:
            lines.append("### Limitations")
            for lim in card.limitations:
                lines.append(f"- {lim}")
            lines.append("")

        if card.examples:
            lines.append("### Examples")
            for ex in card.examples:
                lines.append(f"- {ex}")
            lines.append("")

        lines.append("---")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _build_method_cards_parser() -> argparse.ArgumentParser:
    """Build the method-cards CLI parser."""
    parser = argparse.ArgumentParser(
        prog="comp method-card",
        description="Method Cards — auto-generated documentation for ontology primitives",
    )
    sub = parser.add_subparsers(
        dest="method_card_command", metavar="<command>", required=True
    )

    # list command
    list_parser = sub.add_parser("list", help="List all method cards")
    list_parser.add_argument(
        "--axis",
        choices=["substrate", "geometry", "dynamics", "plasticity", "credit", "update"],
        help="Filter by axis",
    )
    list_parser.add_argument(
        "--internal", action="store_true", help="Include internal primitives"
    )
    list_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )

    # show command
    show_parser = sub.add_parser("show", help="Show a specific method card")
    show_parser.add_argument(
        "axis",
        choices=["substrate", "geometry", "dynamics", "plasticity", "credit", "update"],
        help="Axis name",
    )
    show_parser.add_argument("name", help="Primitive name")
    show_parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format",
    )

    # generate command
    generate_parser = sub.add_parser(
        "generate", help="Generate all method cards to file"
    )
    generate_parser.add_argument("--output", required=True, help="Output file")
    generate_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format",
    )
    generate_parser.add_argument(
        "--axis",
        choices=["substrate", "geometry", "dynamics", "plasticity", "credit", "update"],
        help="Filter by axis",
    )
    generate_parser.add_argument(
        "--internal", action="store_true", help="Include internal primitives"
    )

    return parser


def _print_card_text(card: MethodCard) -> None:
    """Print a single method card in text format."""
    print(f"Axis: {card.axis}")
    print(f"Name: {card.name}")
    print(f"Class: {card.class_name} ({card.module})")
    if card.source_file and card.source_lines:
        print(
            f"Source: {card.source_file}:{card.source_lines[0]}-{card.source_lines[1]}"
        )
    print()
    print("Purpose:")
    print(f"  {card.purpose or 'No description available.'}")
    print()

    if card.config_options:
        print("Configuration Options:")
        for param, info in card.config_options.items():
            default = info.get("default", "required")
            ptype = info.get("type", "Any")
            desc = info.get("description", "")
            print(f"  {param}: {ptype} = {default}")
            if desc:
                print(f"    {desc}")
        print()

    if card.limitations:
        print("Limitations:")
        for lim in card.limitations:
            print(f"  - {lim}")
        print()

    if card.examples:
        print("Examples:")
        for ex in card.examples:
            print(f"  - {ex}")
        print()


def _handle_list(args: argparse.Namespace) -> int:
    """Handle the 'list' subcommand."""
    cards = generate_method_cards(axis=args.axis, include_internal=args.internal)

    if args.format == "text":
        for card in cards:
            print(f"{card.axis:12} {card.name:30} {card.class_name}")
        print(f"\nTotal: {len(cards)} method cards")
    elif args.format == "json":
        data = [
            {
                "axis": c.axis,
                "name": c.name,
                "class_name": c.class_name,
                "module": c.module,
                "purpose": c.purpose,
            }
            for c in cards
        ]
        print(json.dumps(data, indent=2))

    return 0


def _handle_show(args: argparse.Namespace) -> int:
    """Handle the 'show' subcommand."""
    cards = generate_method_cards(axis=args.axis, include_internal=True)
    card = next((c for c in cards if c.name == args.name), None)
    if not card:
        print(f"Method card not found: {args.axis}/{args.name}", file=sys.stderr)
        return 1

    if args.format == "text":
        _print_card_text(card)
    elif args.format == "json":
        data = {
            "axis": card.axis,
            "name": card.name,
            "class_name": card.class_name,
            "module": card.module,
            "purpose": card.purpose,
            "config_options": card.config_options,
            "limitations": card.limitations,
            "examples": card.examples,
            "references": card.references,
            "source_file": card.source_file,
            "source_lines": card.source_lines,
        }
        print(json.dumps(data, indent=2))
    elif args.format == "markdown":
        export_method_cards([card], Path("/dev/stdout"), "markdown")

    return 0


def _handle_generate(args: argparse.Namespace) -> int:
    """Handle the 'generate' subcommand."""
    cards = generate_method_cards(axis=args.axis, include_internal=args.internal)
    export_method_cards(cards, Path(args.output), args.format)
    print(f"Generated {len(cards)} method cards to {args.output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for method-card commands."""
    parser = _build_method_cards_parser()
    args = parser.parse_args(argv)

    handlers = {
        "list": _handle_list,
        "show": _handle_show,
        "generate": _handle_generate,
    }

    handler = handlers.get(args.method_card_command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
