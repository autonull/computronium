"""`comp verify` — verify a primitive's map row in a slice family (TODO95 P5).

The same scanner a stranger runs after the recipe in ``docs/sec/map.md``: it
reads the published map only, so adding a credit never needs the internals.
Exit 1 names the first problem; exit 0 holds the row.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from computronium.experiment.sec_extension import verify_row

app = typer.Typer(add_completion=False, help="Verify a primitive's map row in a slice")
console = Console()


@app.callback(invoke_without_command=True)
def verify(
    primitive: str = typer.Option(
        ..., "--primitive", "-p", help="Primitive ID: primitive.<axis>.<name>"
    ),
    family: str = typer.Option(
        "vision", "--slice", "-s", help="Task family the slice is verified in"
    ),
    map_path: Path = typer.Option(
        Path("results/sec/map.json"), "--map", "-m", help="Map document"
    ),
    as_json: bool = typer.Option(False, "--json", help="Print the verdict as JSON"),
) -> None:
    """Check that a primitive holds a map row in the named slice family."""
    if not map_path.exists():
        typer.echo(f"comp verify: no map at {map_path}", err=True)
        raise typer.Exit(1)
    verdict = verify_row(
        json.loads(map_path.read_text(encoding="utf-8")), primitive, family
    )
    if as_json:
        console.print_json(json.dumps(verdict.to_dict()))
    else:
        state = "held" if verdict.held else "refused"
        console.print(
            f"{verdict.primitive} in {verdict.family}: {state} ({verdict.status})"
        )
        if verdict.held:
            console.print(f"  box: {verdict.box.get('task', '—')}")
            console.print(f"  ruler: {verdict.ruler or '—'}")
            console.print(f"  control: {verdict.control}")
            console.print(f"  measurement: {verdict.measurement}")
            console.print(f"  replay hash: {verdict.replay_hash or '—'}")
        for problem in verdict.problems:
            console.print(f"  problem: {problem}", style="red")
    raise typer.Exit(0 if verdict.held else 1)


if __name__ == "__main__":
    app()
