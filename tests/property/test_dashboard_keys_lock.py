"""The dashboard's keys: one list, and no key claimed twice (TODO71 Phase 0).

The panels, the charts, the control bar and the stage's views all answer to
the keyboard, so the keys they hold are one list. A view that claimed a key
another panel already held would steal it, and the reader would find that the
caption no longer toggles.

The lock reads the browser's own source: the keys are declared in TypeScript,
and a lock that kept its own copy of them would be a second truth.

The binding layer (src/bindings.ts) is now the authoritative source. This lock
parses the binding table AND every view's key field; a key claimed twice
anywhere fails. The free-key list is what keys.ts says.
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


def _bindings_source() -> str:
    return (DASHBOARD_SRC / "bindings.ts").read_text(encoding="utf-8")


def _keys_source() -> str:
    return (DASHBOARD_SRC / "keys.ts").read_text(encoding="utf-8")


def _binding_table() -> list[tuple[str, str, str]]:
    """Every binding in the table: (id, key, group)."""
    text = _bindings_source()
    bindings: list[tuple[str, str, str]] = []
    # Find all binding objects
    for match in re.finditer(r'\{\s*id:\s*"([^"]+)"', text):
        start = match.start()
        obj_text = text[start : start + 500]
        end_idx = 0
        depth = 0
        for i, ch in enumerate(obj_text):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end_idx = i + 1
                    break
        obj = obj_text[:end_idx]
        binding_id = match.group(1)
        key_match = re.search(r'key:\s*"([^"]+)"', obj)
        group_match = re.search(r'group:\s*"([^"]+)"', obj)
        if key_match and group_match:
            bindings.append((binding_id, key_match.group(1).lower(), group_match.group(1)))
    return bindings


def _binding_chords() -> list[tuple[str, str]]:
    """Every chord in the binding table: (binding_id, chord)."""
    text = _bindings_source()
    chords: list[tuple[str, str]] = []
    for match in re.finditer(r'id:\s*"([^"]+)"[^}]*chord:\s*"([^"]+)"', text):
        binding_id = match.group(1)
        chord = match.group(2)
        if chord:
            chords.append((binding_id, chord.lower()))
    return chords


def _view_keys() -> list[tuple[str, str]]:
    """The key each view of the stage names."""
    found: list[tuple[str, str]] = []
    for path in sorted((DASHBOARD_SRC / "stage").glob("*.ts")):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r'^\s*key = "([^"]+)";', text, re.MULTILINE):
            found.append((path.name, match.group(1)))
    return found


def _claims_from_bindings() -> list[tuple[str, str]]:
    """Every key the binding table claims, and the binding id that claims it."""
    claims: list[tuple[str, str]] = []
    for binding_id, key, group in _binding_table():
        if key and key != "escape":
            claims.append((f"binding:{binding_id}", key))
    # Chords are separate key combinations (e.g., "shift+r"), not base letter claims
    for binding_id, chord in _binding_chords():
        if chord:
            claims.append((f"binding:{binding_id}:chord", chord))
    return claims


def _claims_from_views() -> list[tuple[str, str]]:
    """Every key the views claim."""
    claims: list[tuple[str, str]] = []
    for name, key in _view_keys():
        claims.append((f"view:{name}", key.lower()))
    return claims


def _all_claims() -> list[tuple[str, str]]:
    """All claims from bindings and views."""
    claims = []
    claims.extend(_claims_from_bindings())
    claims.extend(_claims_from_views())
    return claims


def test_no_key_is_claimed_twice() -> None:
    """One key, one owner.

    A key claimed twice is a key whose meaning depends on which listener
    answered first, and the reader cannot tell which one it was.
    """
    owners: dict[str, list[str]] = {}
    for owner, key in _all_claims():
        owners.setdefault(key, []).append(owner)
    twice = {key: names for key, names in owners.items() if len(names) > 1}
    assert not twice, f"a key is claimed twice: {twice}"


def test_no_letter_is_free() -> None:
    """The plan says the letters are gone.

    TODO69 left four; TODO70's controls took all four and the spacebar
    besides. A free letter is a letter a future view would take without
    anyone noticing that the panels already wanted it.
    """
    taken = {key for _owner, key in _all_claims() if key in LETTERS}
    free = set(LETTERS) - taken
    assert not free, f"the plan says no letter is free; these are: {sorted(free)}"


def test_each_group_holds_the_letters_the_plan_says() -> None:
    """The groups are named in the plan, and the plan is the lock."""
    panel_keys = {key for _owner, key in _claims_from_bindings() if _owner.startswith("binding:panel-")}
    chart_keys = {key for _owner, key in _claims_from_bindings() if _owner.startswith("binding:chart-")}
    control_keys = {key for _owner, key in _claims_from_bindings() if _owner.startswith("binding:control-")}
    view_keys = {key for _owner, key in _claims_from_views() if key in LETTERS}

    assert panel_keys == PANEL_LETTERS
    assert chart_keys == CHART_LETTERS
    assert control_keys == CONTROL_LETTERS | {" "}, "the spacebar is play and pause"
    assert view_keys == VIEW_LETTERS


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
    owners = []
    for owner, key in _all_claims():
        if key == letter:
            owners.append(owner)
    assert len(owners) == 1, f"{letter} is claimed by {owners}"