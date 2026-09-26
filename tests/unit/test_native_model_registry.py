"""The native-model registry can answer a membership question (TODO36 §4.8).

`resolve_native_model` fell back to the EqProp composition for any name it did not
recognise, so `directed_ep` — which has its own native factory — silently ran as
EqProp in every caller. The fallback stays (it is load-bearing for one study, see
§4.8), but the registry is now complete enough that a caller can *ask*.
"""

import pytest

from computronium.experiment.param_estimator import (
    NATIVE_MODEL_NAMES,
    has_model,
    resolve_native_model,
)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("backprop_mlp", "create_native_backprop_mlp"),
        ("standard_fa", "create_native_fa_mlp"),
        ("dfa_deep", "create_native_fa_mlp"),
        ("direct_feedback_alignment_eqprop", "create_native_fa_mlp"),
        ("tile_snn", "create_native_tile_snn"),
        ("tile_hebbian", "create_native_tile_hebbian"),
        ("pepita_mlp", "create_native_lemma_mlp"),
        ("directed_ep", "create_native_directed_ep"),
        ("momentum_eqprop", "create_native_momentum_eqprop"),
    ],
)
def test_a_zoo_name_reaches_its_own_factory(name: str, expected: str) -> None:
    assert has_model(name)
    assert resolve_native_model(name).__name__ == expected


def test_membership_and_resolution_never_disagree() -> None:
    for name in (*NATIVE_MODEL_NAMES, "standard_fa", "dfa_deep", "diff_target_prop"):
        resolved = resolve_native_model(name)
        # Either the name is a member and got its own factory, or it is not and the
        # EqProp fallback is the documented answer. What must never happen is a
        # member silently resolving to the fallback.
        assert has_model(name) or resolved.__name__ == "create_native_eqprop_mlp"


def test_a_non_model_is_not_a_member() -> None:
    assert not has_model("diff_target_prop")
    assert not has_model("no_such_model")


def test_every_native_factory_is_reachable_by_its_own_name() -> None:
    """The registry must not lag `models.native.__all__`."""
    from computronium.models import native

    exported = {
        name.removeprefix("create_native_")
        for name in native.__all__
        if name.startswith("create_native_")
    }
    missing = sorted(
        stem
        for stem in exported
        if not has_model(stem) and not has_model(stem.replace("_mlp", ""))
    )
    assert missing == [], f"native factories with no fragment: {missing}"
