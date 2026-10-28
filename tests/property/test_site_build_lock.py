"""Documentation-site build lock.

``docs/index.html`` and ``docs/index.md`` are assembled by
``docs/build_site.py`` from three source trees: the slide snippets in
``docs/slides/``, the README sections in ``docs/readme/``, and the cheatsheet
artifacts in ``docs/cheatsheet/``. The lock holds these claims:

1. the committed site and Markdown twin are exactly what the sources build;
2. each set's manifest is the only ordering: every listed item contributes
   one anchor, and no unlisted item hides in the source directory;
3. the cheatsheet viewer's manifest is the SVG's panel index: every panel has
   a target, a bounding box, and a documentation section;
4. every internal route and relative asset resolves;
5. no generated marker or template placeholder survives, and the site makes
   no external resource request;
6. speaker notes live only inside a popover.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import pytest

from tests.property._site import SITE, load_site_builder

HTML = SITE / "index.html"
MARKDOWN = SITE / "index.md"
CHEATSHEET = SITE / "cheatsheet"
CHEATSHEET_SVG = CHEATSHEET / "cheatsheet.svg"
CHEATSHEET_MANIFEST = CHEATSHEET / "panels.json"

builder = load_site_builder()


@lru_cache(maxsize=1)
def _site() -> str:
    return builder.build_site()


@lru_cache(maxsize=1)
def _markdown() -> str:
    return builder.build_index_md()


@lru_cache(maxsize=1)
def _manifest() -> dict[str, object]:
    return json.loads(CHEATSHEET_MANIFEST.read_text(encoding="utf-8"))


def _slide_ids() -> list[str]:
    return re.findall(r'<section class="slide" id="([a-z0-9-]+)"', _site())


def _doc_ids() -> list[str]:
    return re.findall(r'<section class="doc-section" id="docs-([a-z0-9-]+)"', _site())


def _heading_ids() -> set[str]:
    return set(re.findall(r'id="docs-h-([^"]+)"', _site()))


def _panel_keys() -> set[str]:
    return {panel["key"] for panel in _manifest()["panels"]}


@pytest.mark.timeout(300)
class TestSiteBuildLock:
    def test_site_matches_the_build(self) -> None:
        assert HTML.read_text(encoding="utf-8") == _site(), (
            "docs/index.html drifted from the site sources; "
            "run `uv run python docs/build_site.py`"
        )

    def test_markdown_twin_matches_the_build(self) -> None:
        assert MARKDOWN.read_text(encoding="utf-8") == _markdown(), (
            "docs/index.md drifted from the site sources; "
            "run `uv run python docs/build_site.py`"
        )

    def test_sets_are_registered(self) -> None:
        keys = {spec.key for spec in builder.SETS}
        assert keys == {"about", "docs", "cheatsheet"}
        for spec in builder.SETS:
            assert spec.label
            assert spec.icon
            assert f'data-set="{spec.key}"' in _site()

    def test_about_manifest_is_the_only_ordering(self) -> None:
        listed = builder._slide_files()
        assert _slide_ids() == [path.stem for path in listed]
        on_disk = {path.name for path in (SITE / "slides").glob("*.md")}
        assert on_disk - {path.name for path in listed} == {"BRIEF.md"}, (
            "unlisted slide snippet"
        )
        assert len(listed) == len(builder._SLIDES), "duplicate in the slide manifest"

    def test_docs_manifest_is_the_only_ordering(self) -> None:
        expected = [Path(name).stem for name in builder._readme_builder()._SECTIONS]
        assert _doc_ids() == expected

    def test_cheatsheet_manifest_matches_the_svg(self) -> None:
        manifest = _manifest()
        svg = CHEATSHEET_SVG.read_text(encoding="utf-8")
        width = float(re.search(r'width="([\d.]+)"', svg).group(1))
        height = float(re.search(r'height="([\d.]+)"', svg).group(1))
        canvas = manifest["canvas"]
        assert abs(width - canvas["width"]) < 1.0
        assert abs(height - canvas["height"]) < 1.0
        doc_ids = set(_doc_ids())
        for panel in manifest["panels"]:
            assert f'id="panel-{panel["key"]}"' in svg
            assert f'data-panel="{panel["key"]}"' in svg
            assert panel["doc"] in doc_ids, panel["key"]
            assert all(key in panel for key in ("x", "y", "w", "h"))

    def test_internal_routes_resolve(self) -> None:
        slides = set(_slide_ids())
        docs = set(_doc_ids())
        headings = _heading_ids()
        panels = _panel_keys()
        for route in set(re.findall(r'href="(#/[^"]*)"', _site())):
            parts = route[2:].split("/")
            match parts:
                case ["about", slide]:
                    assert slide in slides, route
                case ["docs", section]:
                    assert section in docs, route
                case ["docs", section, heading]:
                    assert section in docs, route
                    assert heading in headings, route
                case ["cheatsheet"]:
                    pass
                case ["cheatsheet", panel]:
                    assert panel in panels, route
                case _:
                    raise AssertionError(f"unknown site route: {route}")

    def test_relative_assets_exist(self) -> None:
        for _, value in re.findall(r'(href|src)="([^"]*)"', _site()):
            if value.startswith(("http://", "https://", "mailto:", "data:", "#", "//")):
                continue
            target = SITE / value.split("#")[0].split("?")[0]
            assert target.exists(), f"missing relative asset: {value}"

    def test_no_external_resource_requests(self) -> None:
        site = _site()
        assert not re.search(r"<script[^>]+src=", site)
        assert not re.search(r"<link[^>]+href=", site)
        assert not re.search(r'<img[^>]+src="https?://', site)
        assert "fetch(" not in site

    def test_no_markers_or_placeholders_survive(self) -> None:
        site = _site()
        assert "<!-- gen:" not in site
        assert "<!-- include:" not in site
        assert "{{" not in site
        assert "{{" not in _markdown()

    def test_plain_anchors_resolve(self) -> None:
        ids = set(re.findall(r'id="([^"]+)"', _site()))
        plain = set(re.findall(r'href="#([^/][^"]*)"', _site()))
        assert plain <= ids, f"unresolved anchors: {sorted(plain - ids)}"

    def test_markdown_twin_carries_every_set(self) -> None:
        markdown = _markdown()
        for heading in ("## About", "## Documentation", "## Cheatsheet"):
            assert heading in markdown

    def test_speaker_notes_never_reach_the_slide_body(self) -> None:
        site = _site()
        for path in builder._slide_files():
            expanded = builder._expand_slide(
                path.read_text(encoding="utf-8"), source=path.name
            )
            notes = builder._NOTES_RE.findall(expanded)
            if not notes:
                continue
            section = re.search(
                rf'<section class="slide" id="{path.stem}".*?</section>', site, re.S
            )
            assert section is not None, path.stem
            stage, _, rest = section.group(0).partition('<div id="notes-')
            assert rest, f"{path.name}: notes must live in a popover"
            assert 'popover="auto"' in rest, path.name
            rendered = builder._renderer().render(notes[0].strip())
            probe = re.sub(r"<[^>]+>", "", rendered).strip()[:60]
            assert probe in rest, f"{path.name}: note text missing from its popover"
            assert probe not in stage, f"{path.name}: note text leaked into the body"
