"""The axis metadata is the registry's (TODO68).

The frontend's axis metadata used to be a hand-written list of primitives, and
it had drifted from the system: it called ``pc_alm`` ``pca_lm`` and
``temporal_psi`` ``stdp``. The registries are the single source, so the
generated file is checked against them: a primitive that changes its name in
the registry changes its name here, and a second list cannot creep back in.
"""

from __future__ import annotations

import json
from pathlib import Path

from computronium.experiment.schema.axis import AXES_REGISTRIES
from computronium.experiment.schema.harvest import AXIS_KIND_ORDER
from computronium.experiment.schema.seed_registries import seed_all_registries

ROOT = Path(__file__).resolve().parents[3]
METADATA = (
    ROOT
    / "computronium"
    / "experiment"
    / "execution"
    / "dashboard"
    / "src"
    / "axis-metadata.json"
)


def _metadata() -> dict:
    seed_all_registries()
    return json.loads(METADATA.read_text(encoding="utf-8"))


def test_the_metadata_holds_every_axis_the_registry_declares() -> None:
    metadata = _metadata()

    assert set(metadata["axes"]) == {axis.value for axis in AXIS_KIND_ORDER}


def test_every_axis_names_the_primitives_its_registry_declares() -> None:
    metadata = _metadata()

    for axis in AXIS_KIND_ORDER:
        declared = [spec.name for spec in AXES_REGISTRIES[axis].values()]
        written = [
            primitive["name"]
            for primitive in metadata["axes"][axis.value]["primitives"]
        ]
        assert written == declared, axis.value


def test_every_axis_has_a_name_a_reader_can_read() -> None:
    metadata = _metadata()

    for axis in AXIS_KIND_ORDER:
        entry = metadata["axes"][axis.value]
        assert entry["display_name"]
        assert entry["description"]


def test_a_primitive_carries_the_registrys_own_description() -> None:
    metadata = _metadata()

    specs = {spec.name: spec for spec in AXES_REGISTRIES[AXIS_KIND_ORDER[0]].values()}
    for primitive in metadata["axes"][AXIS_KIND_ORDER[0].value]["primitives"]:
        spec = specs[primitive["name"]]
        assert primitive["summary"] == spec.description
        assert primitive["available"] == spec.available
