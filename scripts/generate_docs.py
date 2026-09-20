#!/usr/bin/env python
"""Generate documentation from ImplementationSpec metadata.

Renders per-implementation Markdown files and an implementation matrix.

Usage:
    uv run python scripts/generate_docs.py --all --output docs/generated/
    uv run python scripts/generate_docs.py --id primitive.state_dynamics.energy_minimization --output docs/generated/
"""

import argparse
import pathlib
import subprocess  # needed for git SHA and matrix.py invocation
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape

from computronium.acceleration.registry import all_specs

TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates" / "docs"

# ruff: file-ignore[suspicious-subprocess-import,subprocess-without-shell-equals-true,start-process-with-partial-path] (subprocess import/run with fixed args for git SHA and matrix.py)


def _get_git_sha() -> str | None:
    """Get current git SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        return None
    return None


def _render_spec(spec, env: Environment) -> str:
    """Render a single spec to Markdown."""
    template = env.get_template("implementation.md.j2")
    return template.render(spec=spec)


def _write_spec_doc(spec, output_dir: pathlib.Path, env: Environment) -> pathlib.Path:
    """Write a spec's documentation to the output directory."""
    if spec.kind == "primitive" and spec.axis:
        doc_dir = output_dir / "primitives" / spec.axis
    else:
        doc_dir = output_dir / "algorithms"

    doc_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    safe_name = spec.id.replace(".", "_").replace("/", "_")
    output_path = doc_dir / f"{safe_name}.md"

    content = _render_spec(spec, env)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def _generate_matrix_md(output_dir: pathlib.Path) -> pathlib.Path:
    """Generate IMPLEMENTATION_MATRIX.md using matrix.py."""
    output_path = output_dir / "IMPLEMENTATION_MATRIX.md"
    result = subprocess.run(
        [sys.executable, "-m", "computronium.acceleration.matrix", "--format", "github-markdown"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"Warning: matrix.py failed: {result.stderr}", file=sys.stderr)
        content = "# Implementation Matrix\n\n*Generation failed.*\n"
    else:
        content = result.stdout
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate documentation from specs")
    parser.add_argument(
        "--all", action="store_true", help="Generate docs for all registered implementations"
    )
    parser.add_argument(
        "--id", help="Generate docs for a specific implementation ID"
    )
    parser.add_argument(
        "--output",
        default="docs/generated",
        help="Output directory (default: docs/generated)",
    )
    parser.add_argument(
        "--matrix-only", action="store_true", help="Only generate the implementation matrix"
    )

    args = parser.parse_args()

    if not args.all and not args.id and not args.matrix_only:
        parser.error("Either --all, --id, or --matrix-only is required")

    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(),
    )

    specs_to_render = []

    if args.all:
        specs_to_render = list(all_specs())
        print(f"Generating docs for {len(specs_to_render)} implementations...")
    elif args.id:
        try:
            from computronium.acceleration.registry import get
            spec = get(args.id)
            specs_to_render = [spec]
            print(f"Generating docs for {spec.id}...")
        except KeyError:
            print(f"Error: Implementation not found: {args.id}", file=sys.stderr)
            return 1

    # Render individual spec docs
    for spec in specs_to_render:
        try:
            output_path = _write_spec_doc(spec, output_dir, env)
            print(f"  {output_path}")
        except Exception as e:
            print(f"  Error rendering {spec.id}: {e}", file=sys.stderr)

    # Generate matrix
    matrix_path = _generate_matrix_md(output_dir)
    print(f"  {matrix_path}")

    print(f"\nDocumentation generated in {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
