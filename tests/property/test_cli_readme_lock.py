"""CLI ↔ README lock (TODO44 D2).

The README CLI reference table must equal the `comp` dispatcher table:
same command set, one-line purpose per command. Drift fails CI so the
README stays referenceable.
"""

from __future__ import annotations

import re
from pathlib import Path

from computronium.cli.__main__ import _SUBCOMMANDS

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"


def _readme_cli_table() -> dict[str, str]:
    """Parse the §6 CLI reference table: command -> purpose."""
    text = README.read_text(encoding="utf-8")
    section = text.split("## 6. CLI reference", 1)[1].split("## 7.", 1)[0]
    table: dict[str, str] = {}
    for line in section.splitlines():
        m = re.match(r"\| `([\w-]+)` \| (.+) \|$", line.strip())
        if m:
            table[m.group(1)] = m.group(2).strip()
    return table


class TestCliReadmeLock:
    def test_command_set_matches_dispatcher(self) -> None:
        assert set(_readme_cli_table()) == set(_SUBCOMMANDS)

    def test_every_command_has_purpose(self) -> None:
        for command, purpose in _readme_cli_table().items():
            assert purpose, f"{command} has no purpose line"
            assert not purpose.startswith(":--"), f"{command} purpose is placeholder"

    def test_kernel_surface_commands_documented_runnable(self) -> None:
        """The documented kernel surface CLI examples parse against real subcommands."""
        text = README.read_text(encoding="utf-8")
        section = text.split("## 6. CLI reference", 1)[1].split("## 7.", 1)[0]
        for command in re.findall(r"comp report (\w+)", section):
            assert command in {"run", "report", "export", "conformance", "status"}, (
                f"undocumented `comp report {command}` example"
            )
