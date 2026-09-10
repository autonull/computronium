"""Card-drift lock on docs/IDENTITY_CARDS.md.

The generated card body (``scripts/generate_identity_cards.py`` output)
must remain an ordered, stripped subsequence of the published doc. The
doc's header/status prose is the hand-maintained index and is not locked;
every card row keeps full teeth — editing a card in code without
regenerating the doc (or vice versa) fails.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from generate_identity_cards import collect_cards

DOC = Path("docs/IDENTITY_CARDS.md")


def test_identity_cards_doc_matches_generated_body() -> None:
    import io
    from contextlib import redirect_stdout

    cards, missing = collect_cards()
    assert not missing, f"primitives without cards: {missing}"
    from computronium.core.identity_card import IDENTITY_CARD_HEADER

    buf = io.StringIO()
    with redirect_stdout(buf):
        print(IDENTITY_CARD_HEADER, end="")
        for card in cards:
            print(card.to_markdown_row())
    generated = buf.getvalue().splitlines()

    doc_lines = DOC.read_text(encoding="utf-8").splitlines()
    it = iter(line.strip() for line in doc_lines)
    drifted = [line for line in generated if line.strip() not in it]
    assert not drifted, (
        f"{len(drifted)} card lines drifted from {DOC}; regenerate the doc "
        f"with scripts/generate_identity_cards.py. First: {drifted[0]!r}"
    )
