"""Unit tests for proposal composition and task fencing (TODO27 P1.1/P1.4)."""

import pytest

from computronium.autoscientist.compose import (
    ProposalComposeError,
    assert_task_runnable,
    build_geometry_config,
    compose_cell_system,
    compose_proposal_system,
)
from computronium.autoscientist.proposer import ExperimentProposer, cell_key


def test_geometry_override_replaces_topology():
    system = compose_proposal_system(
        "eqprop",
        input_dim=20,
        output_dim=5,
        lr=1e-3,
        geometry={"topology_type": "attention", "depth": 2, "hidden_dim": 32},
    )
    assert system.geometry.config.topology_type == "attention"
    # Family layers ride the base factory unchanged.
    assert system.dynamics.config.dynamics_type == "energy_minimization"


def test_unknown_geometry_key_fails_loudly():
    with pytest.raises(ProposalComposeError, match="bogus"):
        build_geometry_config(
            {"topology_type": "recurrent", "bogus": 1},
            input_dim=8,
            output_dim=2,
        )


def test_unknown_topology_fails_loudly():
    with pytest.raises(ProposalComposeError, match="topology_type"):
        build_geometry_config({"topology_type": "quantum"}, input_dim=8, output_dim=2)


def test_full_cell_composition():
    system = compose_cell_system(
        dynamics="instantaneous",
        credit="pepita",
        update="adam",
        geometry={"topology_type": "recurrent", "depth": 3, "hidden_dim": 32},
        input_dim=10,
        output_dim=3,
    )
    assert system.dynamics.config.dynamics_type == "instantaneous"
    assert system.credit.config.credit_type == "pepita"
    assert system.update.config.update_type == "adam"
    assert system.geometry.config.topology_type == "recurrent"


def test_unknown_cell_axis_fails_loudly():
    with pytest.raises(ProposalComposeError, match="cell axis"):
        compose_cell_system(
            dynamics="no_such_dynamics",
            credit="pepita",
            update="adam",
            geometry={"topology_type": "feedforward"},
            input_dim=10,
            output_dim=3,
        )


@pytest.mark.parametrize(
    "task", ["tiny_shakespeare", "char_ngram", "wikitext2", "penn_treebank"]
)
def test_lm_lane_fenced(task: str):
    with pytest.raises(ProposalComposeError, match="fenced"):
        assert_task_runnable(task)


def test_unknown_task_rejected():
    with pytest.raises(ProposalComposeError, match="Unknown task"):
        assert_task_runnable("not_a_real_task")


@pytest.mark.parametrize("task", ["mnist", "digits", "iris", "cartpole", "cora"])
def test_runnable_tasks_pass(task: str):
    assert_task_runnable(task)


def test_coverage_cells_are_novel_and_deduplicated():
    proposer = ExperimentProposer()
    cells = proposer.propose_coverage_cells(6, task="digits")
    assert len(cells) == 6
    keys = [c.tags[-1] for c in cells]
    assert len(set(keys)) == len(keys)
    assert keys[0] == cell_key(
        "energy_minimization", "thermodynamic_contrast", "euclidean", "feedforward"
    )


def test_bridge_passes_geometry_through():
    from computronium.autoscientist.bridge import (
        AutoScientistBridge,
        ExperimentProposal,
    )

    proposal = ExperimentProposal(
        hypothesis="h",
        model="eqprop",
        task="digits",
        geometry={"topology_type": "recurrent", "depth": 4},
        dynamics="instantaneous",
    )
    config = AutoScientistBridge().proposal_to_task(proposal)
    assert config["geometry"] == {"topology_type": "recurrent", "depth": 4}
    assert config["dynamics"] == "instantaneous"


def test_instrument_triggered_followups():
    from computronium.autoscientist.bridge import ExperimentProposal

    proposer = ExperimentProposer()
    base = ExperimentProposal(
        hypothesis="base cell",
        model="eqprop",
        task="digits",
        geometry={"topology_type": "recurrent", "depth": 2, "hidden_dim": 32},
        dynamics="instantaneous",
        credit="pepita",
        update="adam",
    )
    zero = proposer.propose_instrument_triggered(
        {"layer_norms": {"0.weight": 0.0, "2.weight": 1.0}}, base
    )
    assert len(zero) == 1
    assert zero[0].geometry["depth"] == 10
    assert zero[0].geometry["init_scheme"] == "mupc"
    assert "instrument_triggered" in zero[0].tags

    unreliable = proposer.propose_instrument_triggered(
        {"layer_norms": {"0.weight": 1.0}, "split_half_cosine": {"0.weight": 0.01}},
        base,
    )
    assert len(unreliable) == 1
    assert unreliable[0].hyperparams["batch_size"] == 128

    quiet = proposer.propose_instrument_triggered(
        {"layer_norms": {"0.weight": 1.0}, "split_half_cosine": {"0.weight": 0.9}},
        base,
    )
    assert quiet == []
