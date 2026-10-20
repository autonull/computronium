"""The tour's frames — the pictures of the surfaces outside the canvas (TODO69).

The tour photographs the system from outside the dashboard as well as from
inside it: the gallery's own figures, the report's own plots, and the
commands that answer what the run touched. Each of those is a *frame*, and
a frame is built in one place.

These tests hold the shape of that machinery: every frame names a shot the
tour knows, every frame carries the words a reader needs (a caption, a
provenance, a command line), and the terminal's font is sized so that a
command's whole answer is in the picture rather than half of it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from capture_dashboard_tour import (  # ruff: ignore[module-import-not-at-top-of-file]
    TOUR,
    command_output,
    gallery_frames,
    surface_frames,
)
from dashboard_capture import terminal_font_size  # ruff: ignore[module-import-not-at-top-of-file]

GALLERY = REPO / "docs" / "figures"


def test_gallery_frames_are_figures_of_real_files() -> None:
    """Every gallery frame points at a figure that exists, and says what it is."""
    frames = gallery_frames(GALLERY)
    assert frames, "the gallery has no frames"

    for frame in frames:
        assert frame.kind == "figure"
        assert Path(frame.payload).exists(), frame.payload
        assert frame.caption, frame.name
        assert "gallery" in frame.provenance, frame.name
        assert frame.name in {shot.name for shot in TOUR}, frame.name


def test_surface_frames_name_their_command() -> None:
    """A terminal frame is a command's own words, under the command's name."""
    frames = surface_frames(REPO / "experiment.duckdb")
    assert frames, "there are no surface frames"

    for frame in frames:
        assert frame.kind == "terminal", frame.name
        assert frame.title.startswith("comp "), frame.name
        assert frame.name in {shot.name for shot in TOUR}, frame.name


def test_a_command_output_is_captured_verbatim() -> None:
    """The frame's text is the command's own output, not a paraphrase of it."""
    from computronium.experiment.surface import cli as surface

    text = command_output(
        surface.main,
        [
            "power-analysis",
            "--effect-size",
            "0.5",
            "--solve-for",
            "n",
            "--format",
            "text",
        ],
    )
    assert "Required n per group" in text


def test_the_gallery_frames_are_figures_the_gallery_declares() -> None:
    """Every frame the tour photographs is a figure the gallery declares."""
    import json

    manifest = json.loads((GALLERY / "manifest.json").read_text(encoding="utf-8"))
    declared = {figure["figure_png"] for figure in manifest["figures"]}
    frames = gallery_frames(GALLERY)
    assert frames
    for frame in frames:
        assert Path(frame.payload).name in declared, frame.name


@pytest.mark.parametrize(
    ("body", "expectation"),
    [
        ("one line", "big"),
        ("\n".join(f"line {index}" for index in range(60)), "small"),
    ],
)
def test_the_terminal_font_fits_its_text(body: str, expectation: str) -> None:
    """A long answer is drawn smaller, so that all of it is in the picture."""
    size = terminal_font_size(body)
    assert size >= 8

    lines = len(body.splitlines())
    if expectation == "big":
        assert size == 22
    else:
        assert size < 22
        # The text, at this size, still fits the window it is drawn in.
        assert lines * 1.34 * size <= 1080
