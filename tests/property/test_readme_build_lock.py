"""README build lock (TODO46 §4 item 4).

`README.md` is assembled from the curated snippets in `docs/readme/` by
`docs/readme/build_readme.py`, with every table that can be read from the code
substituted at build time. The lock holds three claims:

1. the committed README is exactly what the snippets build — a snippet edit
   without a rebuild is drift, not a pending change;
2. no snippet carries a `<!-- gen: -->` marker for a block that does not
   exist, and no generated block is left unsubstituted in the output;
3. the generated tables name what the code actually registers, so a table
   cannot advertise a primitive that was retired (the `nca` precedent) or a
   command that was removed.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.property._readme import SNIPPETS, load_readme_builder

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"

build_readme = load_readme_builder()


def _data_rows(table: str) -> list[str]:
    """Table rows minus the header and its separator."""
    return [r for r in table.splitlines() if r.startswith("|") and "---" not in r][1:]


class TestReadmeBuildLock:
    def test_readme_matches_the_build(self) -> None:
        rendered = build_readme.build_readme()
        assert README.read_text(encoding="utf-8") == rendered, (
            "README.md drifted from docs/readme/*.md; "
            "run `uv run python docs/readme/build_readme.py`"
        )

    def test_every_snippet_contributes(self) -> None:
        rendered = build_readme.build_readme()
        for path in build_readme._section_files():
            text = path.read_text(encoding="utf-8").strip()
            assert text, f"{path.name} is empty"
            assert text.splitlines()[0] in rendered, path.name

    def test_manifest_is_the_only_ordering(self) -> None:
        """An unlisted snippet is invisible; a listed one that moved is a typo."""
        listed = {path.name for path in build_readme._section_files()}
        on_disk = {path.name for path in SNIPPETS.glob("*.md")}
        assert on_disk - listed == set(), "snippet missing from the manifest"
        assert len(listed) == len(build_readme._SECTIONS), "duplicate in the manifest"

    def test_generated_markers_all_resolve(self) -> None:
        for path in build_readme._section_files():
            text = path.read_text(encoding="utf-8")
            for name in re.findall(build_readme._GENERATED_RE.pattern, text):
                assert name in build_readme._GENERATORS, (
                    f"{path.name} requests unknown block {name!r}"
                )

    def test_no_marker_survives_the_build(self) -> None:
        assert not build_readme._GENERATED_RE.search(build_readme.build_readme())

    def test_cli_table_names_every_dispatched_command(self) -> None:
        from computronium.cli.__main__ import _SUBCOMMANDS

        table = build_readme._cli_table()
        for command in _SUBCOMMANDS:
            assert f"| `{command}` |" in table, command

    def test_policy_table_names_every_registered_policy(self) -> None:
        from computronium.experiment.execution.policy import POLICY_CATALOG

        table = build_readme._policy_table()
        for name in POLICY_CATALOG:
            assert f"| `{name}` |" in table, name
        rows = _data_rows(table)
        assert len(rows) == len(POLICY_CATALOG), "stale policy row"

    def test_demo_table_names_every_demo_script(self) -> None:
        table = build_readme._demo_table()
        demos = sorted(p.name for p in (REPO / "scripts" / "demos").glob("demo_*.py"))
        assert demos
        for name in demos:
            assert f"| `{name}` |" in table, name
        rows = _data_rows(table)
        assert len(rows) == len(demos), "stale demo row"

    def test_contents_links_resolve_to_a_heading(self) -> None:
        rendered = build_readme.build_readme()
        headings = {
            build_readme._anchor(h)
            for h in re.findall(r"^## (.+)$", rendered, flags=re.M)
        }
        for anchor in re.findall(r"^-\s+\[.+\]\(#(.+)\)$", rendered, flags=re.M):
            assert anchor in headings, f"contents links to a missing #{anchor}"
