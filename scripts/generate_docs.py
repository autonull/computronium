#!/usr/bin/env python
"""Generate documentation from ImplementationSpec metadata.

Renders per-spec Markdown pages and the implementation matrix from the registry,
so the docs cannot name a spec the runtime does not have (TODO91 S1b/S7).

    uv run python scripts/generate_docs.py --all
    uv run python scripts/generate_docs.py --matrix-only
    uv run python scripts/generate_docs.py --all --check
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape

from computronium.acceleration.matrix import render_github_markdown
from computronium.acceleration.registry import all_specs, get

TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates" / "docs"
DEFAULT_OUTPUT = pathlib.Path("docs/generated")
SCOPES = ("primitives", "algorithms")


def _doc_path(spec, output_dir: pathlib.Path) -> pathlib.Path:
    if spec.kind == "primitive" and spec.axis:
        doc_dir = output_dir / "primitives" / spec.axis
    else:
        doc_dir = output_dir / "algorithms"
    return doc_dir / f"{spec.id.replace('.', '_')}.md"


def _targets(output_dir: pathlib.Path, specs: list) -> dict[pathlib.Path, str]:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(),
    )
    template = env.get_template("implementation.md.j2")
    targets = {
        _doc_path(spec, output_dir): template.render(spec=spec) for spec in specs
    }
    targets[output_dir / "IMPLEMENTATION_MATRIX.md"] = render_github_markdown()
    return targets


def _orphans(output_dir: pathlib.Path, targets: dict) -> list[pathlib.Path]:
    return [
        path
        for scope in SCOPES
        for path in (output_dir / scope).rglob("*.md")
        if path not in targets
    ]


def _stale(targets: dict[pathlib.Path, str]) -> list[pathlib.Path]:
    return [
        path
        for path, content in targets.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="render every spec")
    parser.add_argument("--id", help="render one spec by ID")
    parser.add_argument("--matrix-only", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--check",
        action="store_true",
        help="report stale or orphaned pages instead of writing them",
    )
    args = parser.parse_args()

    if not (args.all or args.id or args.matrix_only):
        parser.error("one of --all, --id, --matrix-only is required")

    output_dir = pathlib.Path(args.output)
    if args.matrix_only:
        specs = []
    elif args.id:
        specs = [get(args.id)]
    else:
        specs = list(all_specs())

    targets = _targets(output_dir, specs)
    orphans = [] if args.matrix_only else _orphans(output_dir, targets)

    if args.check:
        for path in sorted([*_stale(targets), *orphans]):
            print(path)
        return 1 if _stale(targets) or orphans else 0

    for path, content in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for path in orphans:
        path.unlink()
    print(f"wrote {len(targets)} files, removed {len(orphans)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
