"""Generate the Algorithm Identity Card table from ontology primitives.

Scans the credit / update / plasticity ontology modules for classes that
carry an ``IDENTITY_CARD`` (``AlgorithmIdentityCard``) and renders a
Markdown table to stdout. With ``--strict`` (the C.1 pre-commit mode),
exits non-zero if any concrete primitive in those families lacks a card.

Usage::

    uv run python scripts/generate_identity_cards.py            # table to stdout
    uv run python scripts/generate_identity_cards.py --strict   # CI gate
"""

from __future__ import annotations

import argparse
import inspect
import sys

from computronium.core.identity_card import (
    IDENTITY_CARD_HEADER,
    AlgorithmIdentityCard,
)
from computronium.ontology import credit as credit_mod
from computronium.ontology import plasticity as plasticity_mod
from computronium.ontology import update as update_mod

_FAMILIES: dict[str, object] = {
    "credit": credit_mod,
    "update": update_mod,
    "plasticity": plasticity_mod,
}

# Protocol/ABC base classes and non-primitive helpers to skip.
_SKIP_NAMES_PREFIX = ("_",)


def _is_concrete_primitive(obj: type) -> bool:
    if getattr(obj, "__protocol_attrs__", None) or getattr(obj, "_is_protocol", False):
        return False
    if inspect.isabstract(obj):
        return False
    return hasattr(obj, "compute_pseudo_gradient") or hasattr(obj, "step")


def _primitive_classes(module: object) -> list[tuple[str, type]]:
    out = []
    for name in dir(module):
        if name.startswith(_SKIP_NAMES_PREFIX):
            continue
        obj = getattr(module, name)
        if isinstance(obj, type) and _is_concrete_primitive(obj):
            out.append((name, obj))
    return sorted(out)


def collect_cards() -> tuple[list[AlgorithmIdentityCard], list[str]]:
    """Return (cards found, primitive names missing a card).

    Aliases (e.g. ``BackpropCredit = GradientCredit``) resolve to the same
    class object and render once; they appear in ``missing`` under every
    exported name until their target class carries a card.
    """
    cards: list[AlgorithmIdentityCard] = []
    missing: list[str] = []
    seen: set[int] = set()
    for family, module in _FAMILIES.items():
        for name, cls in _primitive_classes(module):
            card = getattr(cls, "IDENTITY_CARD", None)
            if isinstance(card, AlgorithmIdentityCard):
                if id(cls) not in seen:
                    seen.add(id(cls))
                    cards.append(card)
            else:
                missing.append(f"{family}.{name}")
    return cards, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any primitive lacks an identity card (C.1 gate).",
    )
    args = parser.parse_args()

    cards, missing = collect_cards()
    print(IDENTITY_CARD_HEADER, end="")
    for card in cards:
        print(card.to_markdown_row())
    if missing:
        print(
            f"\n{len(missing)} primitives without cards: {', '.join(missing)}",
            file=sys.stderr,
        )
    if args.strict and missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
