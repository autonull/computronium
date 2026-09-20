#!/usr/bin/env python
"""Scaffold a new algorithm package with all required files.

Usage:
    uv run python scripts/scaffold_algorithm.py \
        --name directed_ep \
        --family equilibrium_propagation \
        --primitives energy_minimization,random_projections,euclidean \
        --factory create_directed_ep_mlp

This generates a complete algorithm package under
computronium/algorithms/<name>/ with:
- __init__.py
- spec.py
- reference.py
- kernel.py
- cases.py
- factory.py

And corresponding test files under tests/algorithms/<name>/:
- test_reference.py
- test_kernel_parity.py
- test_factory.py
- test_cases.py
"""

import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).parent / "templates" / "algorithm"
DOCS_TEMPLATE_DIR = Path(__file__).parent / "templates" / "docs"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold a new algorithm package")
    parser.add_argument("--name", required=True, help="Algorithm name (snake_case)")
    parser.add_argument(
        "--family",
        required=True,
        help="Algorithm family (e.g., equilibrium_propagation)",
    )
    parser.add_argument(
        "--primitives", required=True, help="Comma-separated list of primitive IDs"
    )
    parser.add_argument(
        "--factory",
        required=True,
        help="Factory function name (e.g., create_directed_ep_mlp)",
    )
    parser.add_argument(
        "--kernel-tech", default="torch_compile", help="Kernel technology"
    )
    parser.add_argument("--summary", default="", help="Short summary for spec")
    parser.add_argument("--equations", default="", help="Equations for spec")
    parser.add_argument(
        "--invariants", default="", help="Comma-separated invariants for spec"
    )
    parser.add_argument("--notes", default="", help="Notes for spec")
    parser.add_argument("--tags", default="", help="Comma-separated tags for spec")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print files without writing"
    )
    parser.add_argument(
        "--docs",
        action="store_true",
        help="Generate docs stub alongside algorithm files",
    )
    return parser


def _build_context(args: argparse.Namespace) -> dict:
    class_name = "".join(word.capitalize() for word in args.name.split("_"))
    primitives_list = [p.strip() for p in args.primitives.split(",") if p.strip()]
    invariants_list = [i.strip() for i in args.invariants.split(",") if i.strip()]
    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    return {
        "name": args.name,
        "class_name": class_name,
        "family": args.family,
        "factory": args.factory,
        "primitives": primitives_list,
        "kernel_tech": args.kernel_tech,
        "spec_id": f"algorithm.{args.name}",
        "spec_name": " ".join(word.capitalize() for word in args.name.split("_")),
        "summary": args.summary or f"{class_name} algorithm.",
        "equations": args.equations,
        "invariants": invariants_list
        or [
            "deterministic under fixed seed",
            "state remains finite",
            "matches reference implementation",
        ],
        "notes": args.notes or "Reference implementation composes primitives.",
        "tags": tags_list or (args.family.split("_"),),
    }


def _load_envs(args: argparse.Namespace) -> tuple[Environment, Environment | None]:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(),
    )
    docs_env = None
    if args.docs:
        docs_env = Environment(
            loader=FileSystemLoader(DOCS_TEMPLATE_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(),
        )
    return env, docs_env


def _get_file_pairs(
    args: argparse.Namespace, env: Environment
) -> list[tuple[Path, object]]:
    algorithm_dir = Path(f"computronium/algorithms/{args.name}")
    test_dir = Path(f"tests/algorithms/{args.name}")

    return [
        (algorithm_dir / "__init__.py", env.get_template("init.py.j2")),
        (algorithm_dir / "spec.py", env.get_template("spec.py.j2")),
        (algorithm_dir / "reference.py", env.get_template("reference.py.j2")),
        (algorithm_dir / "kernel.py", env.get_template("kernel.py.j2")),
        (algorithm_dir / "cases.py", env.get_template("cases.py.j2")),
        (algorithm_dir / "factory.py", env.get_template("factory.py.j2")),
        (test_dir / "test_reference.py", env.get_template("test_reference.py.j2")),
        (
            test_dir / "test_kernel_parity.py",
            env.get_template("test_kernel_parity.py.j2"),
        ),
        (test_dir / "test_factory.py", env.get_template("test_factory.py.j2")),
        (test_dir / "test_cases.py", env.get_template("test_cases.py.j2")),
    ]


class _MockAlgoSpec:
    def __init__(self, ctx: dict) -> None:
        self.id = ctx["spec_id"]
        self.kind = "algorithm"
        self.name = ctx["spec_name"]
        self.axis = None
        self.family = ctx["family"]
        self.status = "reference_only"
        self.kernel_technology = ctx["kernel_tech"]
        self.supported_backends = ("reference", "kernel")
        self.summary = ctx["summary"]
        self.equations = ctx["equations"]
        self.invariants = ctx["invariants"]
        self.notes = ctx["notes"]
        self.tags = ctx["tags"]
        self.reference_entrypoint = (
            f"computronium.algorithms.{ctx['name']}.reference.step"
        )
        self.kernel_entrypoint = f"computronium.algorithms.{ctx['name']}.kernel.step"
        self.parity = type(
            "Parity",
            (),
            {"max_abs_diff": 1e-4, "max_rel_diff": 1e-3, "min_cosine": 0.99},
        )()
        self.evidence_ids = ()
        self.uses_primitives = ctx["primitives"]


def _render_docs(args: argparse.Namespace, ctx: dict, docs_env: Environment) -> None:
    doc_dir = Path("docs/generated/algorithms")
    safe_name = f"algorithm_{args.name}"
    mock_spec = _MockAlgoSpec(ctx)
    doc_content = docs_env.get_template("implementation.md.j2").render(spec=mock_spec)
    if args.dry_run:
        print(f"=== {doc_dir / f'{safe_name}.md'} ===")
        print(doc_content)
    else:
        doc_dir.mkdir(parents=True, exist_ok=True)
        (doc_dir / f"{safe_name}.md").write_text(doc_content)
        print(f"Created: {doc_dir / f'{safe_name}.md'}")


def _write_files(
    file_pairs: list[tuple[Path, object]], ctx: dict, dry_run: bool
) -> None:
    for path, template in file_pairs:
        content = template.render(**ctx)
        if dry_run:
            print(f"=== {path} ===")
            print(content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"Created: {path}")


def _print_success(args: argparse.Namespace) -> None:
    algorithm_dir = Path(f"computronium/algorithms/{args.name}")
    test_dir = Path(f"tests/algorithms/{args.name}")
    print(f"\nAlgorithm '{args.name}' scaffolded successfully!")
    print(f"  Algorithm: {algorithm_dir}")
    print(f"  Tests:     {test_dir}")
    print("\nNext steps:")
    print("  1. Review and customize the generated files")
    print(f"  2. Run tests: uv run pytest {test_dir} -q")
    print("  3. Update algorithm __init__.py exports if needed")


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    ctx = _build_context(args)
    env, docs_env = _load_envs(args)
    file_pairs = _get_file_pairs(args, env)

    if args.docs and docs_env:
        _render_docs(args, ctx, docs_env)

    _write_files(file_pairs, ctx, args.dry_run)

    if not args.dry_run:
        _print_success(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
