import pytest

from computronium.ceec import StoreError, bootstrap

CONFIG_DIR = "configs/ceec"


@pytest.fixture(scope="module")
def bootstrapped_store(tmp_path_factory):
    from computronium.ceec import CEECStore

    tmp = tmp_path_factory.mktemp("bootstrap")
    store = CEECStore(tmp / "ceec.sqlite3", tmp / "artifacts")
    result = bootstrap.bootstrap(store, CONFIG_DIR)
    yield store, result
    store.close()


class TestBootstrap:
    def test_instruments_exist(self, bootstrapped_store):
        _, result = bootstrapped_store
        assert len(result["instruments"]) == 8
        assert "I-FROZEN-THETA-AUDIT" in result["instruments"]

    def test_hypothesis_beliefs_exist(self, bootstrapped_store):
        store, result = bootstrapped_store
        assert "B-H1-ADAPTIVE-LOCAL-INVERSES" in result["beliefs"]
        assert "B-H5-UPDATE-RULE-SPECIALIZATION" in result["beliefs"]
        for belief_id in result["beliefs"]:
            assert store.current_status(belief_id) == "open"
            rev = store.latest_revision(belief_id)
            assert rev is not None and rev.status == "open"

    def test_goals_exist(self, bootstrapped_store):
        _, result = bootstrapped_store
        assert len(result["goals"]) == 5
        assert "G-EPISTEMIC-HEALTH" in result["goals"]

    def test_experiments_pre_registered(self, bootstrapped_store):
        store, result = bootstrapped_store
        assert len(result["experiments"]) == 5
        for experiment in store.experiments_by_status("pre_registered"):
            assert experiment.status == "pre_registered"

    def test_no_belief_lacks_scope_or_evidence(self, bootstrapped_store):
        from computronium.ceec import audit

        store, _ = bootstrapped_store
        findings = [
            f
            for f in audit.run_audit(store)
            if f.check in {"belief_without_evidence", "belief_without_scope"}
        ]
        assert findings == []

    def test_double_bootstrap_refused(self, bootstrapped_store):
        store, _ = bootstrapped_store
        with pytest.raises(StoreError, match="already bootstrapped"):
            bootstrap.bootstrap(store, CONFIG_DIR)
