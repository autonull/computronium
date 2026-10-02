"""CLI ↔ README lock (TODO44 D2, TODO46 §4 item 4, D20–D22).

Two claims are locked here, both of which a command *table* cannot establish:

1. every `comp` command in the README is a real, dispatched command;
2. **every documented invocation resolves** — the fenced `bash` blocks are
   parsed against the real parsers, so a documented command that does not
   exist is a test failure rather than a review question (TODO46 D20).

And the tier-0 costs the whole plan depends on are asserted here too: a
`--dry-run` writes nothing and prints something (D22), and a read command
against a store that does not exist exits non-zero without a traceback (D21).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from computronium.cli.__main__ import _SUBCOMMANDS
from computronium.cli.__main__ import main as dispatcher_main
from computronium.experiment.surface import cli as surface_cli
from tests.property._readme import load_readme_builder

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"


def _readme() -> str:
    return README.read_text(encoding="utf-8")


def _bash_blocks(text: str) -> list[list[str]]:
    """Command lines from every fenced ``bash`` block, comments stripped."""
    blocks: list[list[str]] = []
    in_block = False
    lines: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("```"):
            if in_block:
                blocks.append(lines)
                lines = []
            in_block = not in_block
            continue
        if not in_block:
            continue
        command = line.split("#", 1)[0].strip()
        if command:
            lines.append(command)
    return blocks


def _documented_comp_invocations() -> list[list[str]]:
    """Every ``comp ...`` invocation documented in the README, in order."""
    invocations: list[list[str]] = []
    for block in _bash_blocks(_readme()):
        for command in block:
            parts = command.split()
            if parts[:1] == ["uv"]:
                parts = parts[1:]
                if parts[:1] == ["run"]:  # ``uv run comp …``
                    parts = parts[1:]
            if parts and parts[0] == "comp":
                invocations.append(parts[1:])
    return invocations


class TestCliReadmeLock:
    def test_every_dispatched_command_is_documented(self) -> None:
        """The README's command table is built from the dispatcher, not typed."""
        builder = load_readme_builder()
        table = builder._cli_table()
        documented = set(re.findall(r"\| `([\w-]+)` \|", table))
        assert documented == set(_SUBCOMMANDS)

    def test_every_command_has_a_purpose(self) -> None:
        builder = load_readme_builder()
        for row in builder._cli_table().splitlines()[2:]:
            purpose = row.rsplit("|", 2)[1].strip()
            assert purpose and not purpose.startswith(":--"), row


class TestDocumentedInvocationsResolve:
    """A documented command that does not exist is D20, and it is a test failure."""

    def test_readme_documents_at_least_one_invocation(self) -> None:
        assert len(_documented_comp_invocations()) >= 3

    @pytest.mark.parametrize(
        "argv", _documented_comp_invocations(), ids=lambda a: " ".join(a) or "comp"
    )
    def test_documented_invocation_resolves(self, argv: list[str]) -> None:
        assert argv, "documented invocation is empty"
        if argv[0] in {"-h", "--help"}:  # the dispatcher's own help is not a command
            assert dispatcher_main(argv) == 0
            return
        command, rest = argv[0], argv[1:]
        assert command in _SUBCOMMANDS, f"`comp {command}` is not in the dispatcher"

        surface_cli._build_parser().parse_args([*_SUBCOMMANDS[command][2], *rest])


class TestTierZeroIsReal:
    """§6.1's cheapest gate only exists if dry-run and status are honest."""

    def test_dry_run_prints_a_plan_and_writes_nothing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        store = tmp_path / "experiment.duckdb"
        code = surface_cli.main([
            "run",
            "quick-verify",
            "--dry-run",
            "--store",
            str(store),
        ])
        assert code == 0
        out = capsys.readouterr().out
        assert "task(s): digits" in out
        assert "legal cell(s)" in out
        assert not store.exists(), "a dry run created the store (D22)"
        assert list(tmp_path.iterdir()) == [], "a dry run wrote to disk (D22)"

    def test_status_on_absent_store_fails_without_traceback(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        code = surface_cli.main(["status", "--store", str(tmp_path / "absent.duckdb")])
        captured = capsys.readouterr()
        assert code == 1, "a status command with no store reported success (D21)"
        assert "No store at" in captured.err
        assert "Traceback" not in captured.err
