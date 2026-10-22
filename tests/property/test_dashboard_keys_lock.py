"""The dashboard's keys: one list, and no key claimed twice (TODO70).

The panels, the charts, the control bar and the stage's views all answer to
the keyboard, so the keys they hold are one list. A view that claimed a key
another panel already held would steal it, and the reader would find that the
caption no longer toggles.

The lock reads the browser's own source: the keys are declared in TypeScript,
and a lock that kept its own copy of them would be a second truth.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

DASHBOARD_SRC = (
    Path(__file__).resolve().parents[2]
    / "computronium"
    / "experiment"
    / "execution"
    / "dashboard"
    / "src"
)

LETTERS = "abcdefghijklmnopqrstuvwxyz"

# The punctuation a new view takes, in the order the plan offers it.
PUNCTUATION = [",", ".", "/", ";", "'"]

# The letters each group holds, as the plan records them.
PANEL_LETTERS = {"h", "r", "c", "q"}
CHART_LETTERS = {"p", "a", "s"}
CONTROL_LETTERS = {"x", "w", "z"}
VIEW_LETTERS = {
    "t",
    "l",
    "d",
    "f",
    "e",
    "y",
    "j",
    "m",
    "b",
    "n",
    "u",
    "g",
    "i",
    "k",
    "o",
}


def _keys_source() -> str:
    return (DASHBOARD_SRC / "keys.ts").read_text(encoding="utf-8")


def _object_keys(name: str) -> list[tuple[str, str]]:
    """The entries of a key object in ``keys.ts``."""
    match = re.search(
        rf"export const {name} = \{{(.*?)\}} as const;",
        _keys_source(),
        re.DOTALL,
    )
    assert match is not None, f"keys.ts has no {name}"
    return re.findall(r'(\w+):\s*"([^"]*)"', match.group(1))


def _view_keys() -> list[tuple[str, str]]:
    """The key each view of the stage names."""
    found: list[tuple[str, str]] = []
    for path in sorted((DASHBOARD_SRC / "stage").glob("*.ts")):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r'^\s*key = "([^"]+)";', text, re.MULTILINE):
            found.append((path.name, match.group(1)))
    return found


def _claims() -> list[tuple[str, str]]:
    """Every key the dashboard claims, and the group that claims it."""
    claims: list[tuple[str, str]] = []
    for name, key in _object_keys("PANEL_KEYS"):
        claims.append((f"panel:{name}", key))
    for name, key in _object_keys("TAB_KEYS"):
        claims.append((f"chart:{name}", key))
    for name, key in _object_keys("CONTROL_KEYS"):
        claims.append((f"control:{name}", key))
    cycle = re.search(r'export const CYCLE_KEY = "([^"]*)"', _keys_source())
    assert cycle is not None, "keys.ts has no CYCLE_KEY"
    claims.append(("cycle", cycle.group(1)))
    for name, key in _view_keys():
        claims.append((f"view:{name}", key))
    return claims


def test_no_key_is_claimed_twice() -> None:
    """One key, one owner.

    A key claimed twice is a key whose meaning depends on which listener
    answered first, and the reader cannot tell which one it was.
    """
    owners: dict[str, list[str]] = {}
    for owner, key in _claims():
        owners.setdefault(key, []).append(owner)
    twice = {key: names for key, names in owners.items() if len(names) > 1}
    assert not twice, f"a key is claimed twice: {twice}"


def test_no_letter_is_free() -> None:
    """The plan says the letters are gone.

    TODO69 left four; TODO70's controls took all four and the spacebar
    besides. A free letter is a letter a future view would take without
    anyone noticing that the panels already wanted it.
    """
    taken = {key for _owner, key in _claims() if key in LETTERS}
    free = set(LETTERS) - taken
    assert not free, f"the plan says no letter is free; these are: {sorted(free)}"


def test_each_group_holds_the_letters_the_plan_says() -> None:
    """The groups are named in the plan, and the plan is the lock."""
    panels = {key for _name, key in _object_keys("PANEL_KEYS")}
    charts = {key for _name, key in _object_keys("TAB_KEYS")}
    controls = {key for _name, key in _object_keys("CONTROL_KEYS")}
    views = {key for _name, key in _view_keys()}
    assert panels == PANEL_LETTERS
    assert charts == CHART_LETTERS
    assert controls == CONTROL_LETTERS | {" "}, "the spacebar is play and pause"
    assert views == VIEW_LETTERS


def test_the_punctuation_list_is_the_one_the_plan_says() -> None:
    """The next view takes a punctuation key, and the list says which."""
    match = re.search(
        r"export const PUNCTUATION_KEYS[^=]*=\s*\[(.*?)\];",
        _keys_source(),
        re.DOTALL,
    )
    assert match is not None, "keys.ts has no PUNCTUATION_KEYS"
    listed = re.findall(r'"([^"]*)"', match.group(1))
    assert listed == PUNCTUATION


@pytest.mark.parametrize("letter", LETTERS)
def test_every_letter_belongs_to_someone(letter: str) -> None:
    """Each letter is claimed, and the reader can find out by whom."""
    owners = [owner for owner, key in _claims() if key == letter]
    assert len(owners) == 1, f"{letter} is claimed by {owners}"
