"""Recipe cards: static registry of recorded credit x update verdicts.

Each card is a measurement-backed verdict (TODO16 §0.3). Sources are the
I(C,U) ladder logs and promotion rounds; cite the log, do not re-run.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecipeCard:
    family: str
    update: str
    status: str
    delta: float | None = None
    parity: float | None = None
    mechanism: str | None = None
    geometries: tuple[str, ...] = ("mlp",)
    edge: str | None = None


RECIPE_CARDS: dict[tuple[str, str], RecipeCard] = {
    ("fa", "muon"): RecipeCard(
        "fa", "muon", "rescue", delta=0.46, geometries=("mlp", "lattice")
    ),
    ("fa", "ortho_adam"): RecipeCard(
        "fa", "ortho_adam", "rescue_sharp", delta=0.36, edge="1e-4 to 1e-3"
    ),
    ("pepita", "adam"): RecipeCard("pepita", "adam", "home", parity=0.884),
    ("pepita", "muon"): RecipeCard("pepita", "muon", "harm", delta=-0.14),
    ("lemma", "*"): RecipeCard("lemma", "*", "closed", mechanism="alignment_noise"),
    ("stdp", "*"): RecipeCard("stdp", "*", "closed", mechanism="no_error_term"),
    ("local_contrastive", "muon"): RecipeCard(
        "local_contrastive", "muon", "boundary", mechanism="gate_shutdown"
    ),
    ("eqprop", "*"): RecipeCard(
        "eqprop", "*", "peak_collapse", mechanism="harvest_required"
    ),
    ("ff", "*"): RecipeCard("ff", "*", "depth_wall_d2", mechanism="harvest_limited"),
}


def lookup(family: str, update: str) -> RecipeCard | None:
    """Exact-card lookup with wildcard fallback."""
    card = RECIPE_CARDS.get((family, update))
    return card if card is not None else RECIPE_CARDS.get((family, "*"))


__all__ = ["RECIPE_CARDS", "RecipeCard", "lookup"]
