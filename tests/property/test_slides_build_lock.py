"""Slides build lock.

``docs/slides.html`` is assembled from the curated snippets in ``docs/slides/``
by ``docs/slides/build_slides.py``. The lock holds four claims:

1. the committed deck is exactly what the snippets build — a snippet edit
   without a rebuild is drift, not a pending change;
2. the manifest is the only ordering: every listed snippet contributes one
   section, its filename is its anchor, and no unlisted snippet hides in the
   directory;
3. every marker resolves — no ``gen:`` block, ``include:`` path, or template
   placeholder survives the build;
4. speaker notes never leak into the slide body: they exist only inside a
   popover, which is what keeps the deck presentable in print.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from tests.property._slides import SNIPPETS, load_slides_builder

REPO = Path(__file__).resolve().parents[2]
DECK = REPO / "docs" / "slides.html"

build_slides = load_slides_builder()


@lru_cache(maxsize=1)
def _deck() -> str:
    return build_slides.build_slides()


class TestSlidesBuildLock:
    def test_deck_matches_the_build(self) -> None:
        assert DECK.read_text(encoding="utf-8") == _deck(), (
            "docs/slides.html drifted from docs/slides/*.md; "
            "run `uv run python docs/slides/build_slides.py`"
        )

    def test_every_snippet_contributes_one_section(self) -> None:
        ids = re.findall(r'<section id="([a-z0-9-]+)"', _deck())
        expected = [path.stem for path in build_slides._section_files()]
        assert ids == expected, "deck sections are not the manifest, in order"

    def test_manifest_is_the_only_ordering(self) -> None:
        listed = [path.name for path in build_slides._section_files()]
        on_disk = {path.name for path in SNIPPETS.glob("*.md")}
        assert on_disk - set(listed) == set(), "snippet missing from the manifest"
        assert len(listed) == len(build_slides._SLIDES), "duplicate in the manifest"

    def test_generated_markers_all_resolve(self) -> None:
        generators = build_slides._generators()
        for path in build_slides._section_files():
            for name in re.findall(build_slides._GEN_RE.pattern, path.read_text()):
                assert name in generators, f"{path.name}: unknown gen:{name}"

    def test_includes_stay_inside_the_snippet_directory(self) -> None:
        for path in build_slides._section_files():
            text = path.read_text(encoding="utf-8")
            for relative in re.findall(build_slides._INCLUDE_RE.pattern, text):
                included = (SNIPPETS / relative).resolve()
                assert included.is_relative_to(SNIPPETS), relative
                assert included.is_file(), f"{path.name}: missing include {relative}"

    def test_no_marker_or_placeholder_survives(self) -> None:
        deck = _deck()
        assert "<!-- gen:" not in deck
        assert "<!-- include:" not in deck
        assert "{{" not in deck

    def test_speaker_notes_never_reach_the_slide_body(self) -> None:
        deck = _deck()
        for path in build_slides._section_files():
            notes = build_slides._NOTES_RE.findall(path.read_text(encoding="utf-8"))
            if not notes:
                continue
            section = re.search(rf'<section id="{path.stem}".*?</section>', deck, re.S)
            assert section is not None, path.stem
            stage, _, rest = section.group(0).partition('<div id="notes-')
            assert rest, f"{path.name}: notes must live in a popover"
            assert 'popover="auto"' in rest, path.name
            rendered = build_slides._renderer().render(notes[0].strip())
            probe = re.sub(r"<[^>]+>", "", rendered).strip()[:60]
            assert probe in rest, f"{path.name}: note text missing from its popover"
            assert probe not in stage, f"{path.name}: note text leaked into the body"
