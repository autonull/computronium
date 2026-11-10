"""`comp capabilities` command — show registered capabilities (B8)."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilityKind,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

app = typer.Typer(help="Show registered capabilities")
console = Console()


@app.command("list")
def list_capabilities(
    kind: CapabilityKind | None = typer.Option(
        None, "--kind", "-k", help="Filter by capability kind"
    ),
    stage: str | None = typer.Option(None, "--stage", "-s", help="Filter by stage"),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json"
    ),
) -> None:
    """List all registered capabilities."""
    seed_all_registries()

    caps = list(CAPABILITIES_REGISTRY.values())

    if kind:
        caps = [c for c in caps if c.kind == kind]
    if stage:
        caps = [c for c in caps if c.stage == stage]

    if format == "json":
        console.print(json.dumps([c.to_dict() for c in caps], indent=2))
        return

    table = Table(title=f"Capabilities ({len(caps)} registered)")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Kind", style="yellow")
    table.add_column("Stage", style="magenta")
    table.add_column("Required", style="red")
    table.add_column("Owner", style="blue")
    table.add_column("Description")

    for cap in caps:
        table.add_row(
            cap.capability_id,
            cap.name,
            cap.kind.value,
            cap.stage,
            "✓" if cap.required else "✗",
            cap.owner,
            cap.description[:80] + "..."
            if len(cap.description) > 80
            else cap.description,
        )

    console.print(table)


@app.command("verify")
def verify_capabilities(
    stage: str | None = typer.Option(
        None, "--stage", "-s", help="Verify specific stage"
    ),
) -> None:
    """Verify capability coverage for a stage or all stages."""
    seed_all_registries()

    caps = list(CAPABILITIES_REGISTRY.values())
    if stage:
        caps = [c for c in caps if c.stage == stage]

    # Group by stage
    stages: dict[str, list] = {}
    for cap in caps:
        stages.setdefault(cap.stage, []).append(cap)

    console.print(f"\n[bold]Capability Coverage[/bold] ({len(caps)} total)")

    for stage_name, stage_caps in sorted(stages.items()):
        required = [c for c in stage_caps if c.required]
        optional = [c for c in stage_caps if not c.required]

        console.print(
            f"\n  [cyan]{stage_name}[/cyan]: {len(stage_caps)} capabilities ({len(required)} required, {len(optional)} optional)"
        )

        missing_required = []
        for cap in required:
            if cap.verifying_test:
                console.print(
                    f"    ✓ {cap.capability_id} ({cap.name}) - test: {cap.verifying_test}"
                )
            else:
                missing_required.append(cap)
                console.print(
                    f"    ⚠ {cap.capability_id} ({cap.name}) - NO VERIFYING TEST"
                )

        for cap in optional:
            console.print(f"    • {cap.capability_id} ({cap.name}) [optional]")

    if stage:
        req = len([c for c in caps if c.required])
        has_test = len([c for c in caps if c.required and c.verifying_test])
        console.print(
            f"\n  Required: {req}, With tests: {has_test}, Missing: {req - has_test}"
        )


@app.command("matrix")
def capability_matrix() -> None:
    """Show capability × stage matrix."""
    seed_all_registries()

    caps = list(CAPABILITIES_REGISTRY.values())

    stages = sorted({c.stage for c in caps})
    kinds = sorted({c.kind for c in caps})

    table = Table(title="Capability Matrix (Kind × Stage)")
    table.add_column("Kind", style="cyan")
    for stage in stages:
        table.add_column(stage, style="green")

    for kind in kinds:
        row = [kind.value]
        for stage in stages:
            count = len([c for c in caps if c.kind == kind and c.stage == stage])
            req_count = len([
                c for c in caps if c.kind == kind and c.stage == stage and c.required
            ])
            cell = f"{count}" + (f" ({req_count} req)" if req_count else "")
            table.add_row(*row) if stage == stages[0] else table.add_row(
                *row
            ) if False else None
            # Rich table needs add_row for each row
            # We'll build differently

    # Rebuild properly
    table = Table(title="Capability Matrix (Kind × Stage)")
    table.add_column("Kind", style="cyan")
    for stage in stages:
        table.add_column(stage, justify="center")

    for kind in kinds:
        cells = []
        for stage in stages:
            count = len([c for c in caps if c.kind == kind and c.stage == stage])
            req_count = len([
                c for c in caps if c.kind == kind and c.stage == stage and c.required
            ])
            cells.append(f"{count}" + (f" ({req_count} req)" if req_count else "0"))
        table.add_row(kind.value, *cells)

    console.print(table)


if __name__ == "__main__":
    app()
