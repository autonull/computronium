"""The probe driver's contract: the metrics a sweep and the parity gate read.

``CoreTrainerDriver`` had no tests at all while reaching training through
``CoreTrainer``, which Sprint 7.6.10 removed -- so every call raised
``ImportError`` and nothing noticed, because nothing called it either. These
are the keys ``scripts/broad_sweep.py`` and
``computronium/validation/backprop_parity.py`` read, asserted against a real
run rather than a fake trainer: the point of the port is that the numbers
come from a system that trained.
"""

from __future__ import annotations

import pytest

from computronium.core.rules import (
    MODEL_NAME_RULES,
    RULE_SYSTEM_CONFIG_KEYS,
    rule_for_name,
    rule_system_from_config,
)
from computronium.experiment.probe import CoreTrainerDriver, _dominant_training_path

_TASK = "iris"
_CONFIG = {"hidden_dim": 8, "num_layers": 1, "learning_rate": 1e-3}


@pytest.fixture
def driver() -> CoreTrainerDriver:
    return CoreTrainerDriver(batch_size=16, record_results=False)


def _probe(driver: CoreTrainerDriver, model: str = "ep", **kwargs: object) -> dict:
    return driver.train(
        model=model,
        task=_TASK,
        config=dict(_CONFIG),
        seed=0,
        epochs=1,
        device="cpu",
        **kwargs,  # type: ignore[arg-type]
    )


def test_a_probe_reports_the_metrics_its_consumers_read(
    driver: CoreTrainerDriver,
) -> None:
    """Every key broad_sweep and backprop_parity index into must be present."""
    metrics = _probe(driver)

    for key in (
        "final_acc",
        "final_train_loss",
        "epoch_time_s",
        "wall_time_s",
        "param_count",
        "forward_flops",
        "backward_flops",
        "peak_memory_mb",
        "best_epoch_acc",
        "acc_at_half",
        "loss_epoch_0",
        "loss_epoch_final",
        "training_paths",
        "training_path",
        "epoch_time_budget_stopped",
        "phantom_knobs",
        "resource_metrics_unavailable",
    ):
        assert key in metrics, f"probe metrics lost {key!r}, a consumer reads it"

    assert metrics["epoch_time_s"] > 0.0
    assert metrics["forward_flops"] > 0
    assert metrics["epoch_time_budget_stopped"] is False


def test_the_reported_path_is_the_rule_that_ran(
    driver: CoreTrainerDriver,
) -> None:
    """``training_path`` is the credit route, and a rule lane cannot say bptt."""
    metrics = _probe(driver, model="hebbian")

    paths = metrics["training_paths"]
    assert isinstance(paths, dict)
    assert paths, "a trained probe recorded no credit-assignment route"
    assert sum(paths.values()) > 0  # type: ignore[arg-type]
    assert metrics["training_path"] == _dominant_training_path(paths)
    assert metrics["training_path"] != "bptt"


def test_a_propagator_overrides_the_model_names_rule(
    driver: CoreTrainerDriver,
) -> None:
    """A family is forced onto a rule its own arm would not otherwise use."""
    native = _probe(driver, model="ep")
    forced = _probe(driver, model="ep", propagator="feedback_alignment")

    assert native["training_path"] != forced["training_path"]


def test_unmeasurable_resources_are_named_not_zeroed(
    driver: CoreTrainerDriver,
) -> None:
    """A CPU run cannot measure CUDA peak memory, and must say so."""
    metrics = _probe(driver)

    assert "peak_memory_mb" in metrics["resource_metrics_unavailable"]  # type: ignore[operator]


def test_an_unroutable_model_name_fails_with_the_known_rules() -> None:
    """A name that is not a rule must not quietly train with backprop."""
    driver = CoreTrainerDriver(batch_size=16, record_results=False)

    with pytest.raises(KeyError) as excinfo:
        _probe(driver, model="not_a_rule_or_model")

    message = str(excinfo.value)
    assert "ep" in message and "hebbian" in message


def test_a_sampled_knob_the_arm_cannot_use_is_reported_as_phantom(
    driver: CoreTrainerDriver,
) -> None:
    """Sampled keys outside the rule system's contract are surfaced."""
    metrics = driver.train(
        model="ep",
        task=_TASK,
        config={**_CONFIG, "feedback_mode": "random"},
        seed=0,
        epochs=1,
        device="cpu",
    )

    assert metrics["phantom_knobs"] == ["feedback_mode"]


def test_every_zoo_model_name_resolves_to_a_rule() -> None:
    """The two vocabularies the sweeps use must both reach a rule."""
    rules = {rule_for_name(name) for name in MODEL_NAME_RULES}
    for name in MODEL_NAME_RULES:
        assert rule_for_name(name) in rules
    assert rule_for_name("feedback_alignment") == "fa"
    assert rule_for_name("contrastive_hebbian_learning") == "hebbian"


def test_rule_config_keys_are_the_ones_a_config_can_carry() -> None:
    """The delivered-key set is the whole contract, not a growing literal."""
    assert set(RULE_SYSTEM_CONFIG_KEYS) == {"hidden_dim", "num_layers", "learning_rate"}


def test_phantom_keys_are_reported_from_the_config_not_a_literal() -> None:
    """A config key the rule system ignores is named, whatever it is."""
    _, phantom = rule_system_from_config("ep", 4, 3, {"hidden_dim": 4, "brand_new": 1})

    assert phantom == ["brand_new"]
