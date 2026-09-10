"""Semantic lock on ``CreditAssignment.requires_autograd``.

``requires_autograd`` decides whether the pipeline settles under
``torch.no_grad`` (``core/pipeline.py``) — flipping it silently detaches
(or needlessly preserves) the settle graph. The R6 regression: FA's
``RandomProjectionsCredit`` lost its ``True`` and every FA family became
a silent zero-gradient no-op. A flip is an API-semantics change; this
lock fails on any undeclared change so it must be made deliberately
here, with the affected credit's docstring updated in the same commit.

Credits that build their OWN graph inside ``compute_pseudo_gradient``
(PepitaCredit, LocalContrastiveCredit, LocalGoodnessCredit's layered
path) legitimately declare False — the settle graph is irrelevant to
them. The declared set below is the frozen contract, not a heuristic.
"""

from __future__ import annotations

import computronium.ontology.credit as credit_module

_REQUIRES_AUTOGRAD_TRUE = frozenset({
    "RandomProjectionsCredit",
    "LocalGoodnessCredit",
    # LemmaCredit subclasses LocalGoodnessCredit (inherits True).
    "LemmaCredit",
    "TargetInversionCredit",
    "GradientCredit",
    # BackpropCredit is an alias of GradientCredit (same class object).
    "BackpropCredit",
})


def test_requires_autograd_contract_frozen():
    """The declared requires_autograd set must match the frozen contract."""
    declared_true = {
        name
        for name, obj in vars(credit_module).items()
        if isinstance(obj, type)
        and hasattr(obj, "requires_autograd")
        and obj.requires_autograd is True
        and getattr(obj, "__module__", "") == credit_module.__name__
    }
    assert declared_true == _REQUIRES_AUTOGRAD_TRUE, (
        "requires_autograd semantics changed. If deliberate, update "
        "_REQUIRES_AUTOGRAD_TRUE here AND the credit's docstring contract "
        "in the same commit; the settle graph is detached for every credit "
        "not in the set (FA went silently inert when this flipped)."
    )
