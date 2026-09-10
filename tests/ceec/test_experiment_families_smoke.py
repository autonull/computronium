"""Smoke test: the five pre-registered experiment families are CEEC-complete."""

import pytest

from computronium.ceec import audit, bootstrap
from computronium.ceec.store import CEECStore


@pytest.fixture(scope="module")
def store(tmp_path_factory):
    s = CEECStore(
        tmp_path_factory.mktemp("families") / "ceec.sqlite3",
        tmp_path_factory.mktemp("families") / "artifacts",
    )
    bootstrap.bootstrap(s, "configs/ceec")
    yield s
    s.close()


EXPECTED_FAMILIES = {
    "X-ALI-001": ["B-H1-ADAPTIVE-LOCAL-INVERSES"],
    "X-TPC-001": ["B-H2-TEMPORAL-PSI-CREDIT"],
    "X-STA-001": ["B-H3-STABLE-TRANSIENT-AMPLIFICATION"],
    "X-RSE-001": ["B-H4-ROUTING-SPARSITY-EFFICIENCY"],
    "X-USU-001": ["B-H5-UPDATE-RULE-SPECIALIZATION"],
}


class TestExperimentFamilies:
    def test_all_five_pre_registered_with_targets(self, store):
        for experiment_id, beliefs in EXPECTED_FAMILIES.items():
            experiment = store.get_experiment(experiment_id)
            assert experiment.status == "pre_registered", experiment_id
            assert experiment.target_beliefs == beliefs, experiment_id
            assert experiment.prediction_probability is not None, experiment_id
            assert experiment.controls, experiment_id
            assert experiment.hard_gates, experiment_id

    def test_frozen_theta_gate_declared_for_psi_family(self, store):
        experiment = store.get_experiment("X-TPC-001")
        assert "frozen_theta_audit" in experiment.hard_gates

    def test_bootstrapped_state_audits_clean(self, store):
        violations = [f for f in audit.run_audit(store) if f.severity == "violation"]
        assert violations == []
