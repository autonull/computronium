"""Recipe: the map document is a projection of ``map.json`` (TODO95 P5).

The committed ``docs/sec/map.md`` is generated, so the generator is the test:
every row, its box, ruler, control and replay hash, both layers, and the
extension recipe appear — and no number comes from a second tally.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.experiment.documentation.sec_map import (
    render_map,
    write_map_document,
)

if TYPE_CHECKING:
    from pathlib import Path


def _map() -> dict:
    rows = {}
    for primitive, axis, val_acc, status in [
        ("primitive.credit_assignment.target_inversion", "credit", 0.1195, "measured"),
        ("primitive.geometry.conv", "geometry", 0.1217, "measured"),
        ("primitive.substrate.analog", "substrate", None, "defective"),
        ("primitive.plasticity.null", "plasticity", None, "refused"),
    ]:
        row = {
            "primitive": primitive,
            "axis": axis,
            "status": status,
            "binding": "bound" if status == "measured" else None,
            "task": "mnist" if status == "measured" else None,
            "ruler": "val_acc on mnist" if status == "measured" else None,
            "rule": "base box" if status == "measured" else None,
            "box": {"task": "mnist"} if status == "measured" else {},
            "control": {"val_acc": 0.89} if status == "measured" else None,
            "measurement": (
                {"val_acc": val_acc, "loss": 1.0} if val_acc is not None else None
            ),
            "resource": {"walltime_s": 1.0},
            "swapped": False,
            "defect": "param_count 999999 over ceiling"
            if status == "defective"
            else None,
            "trigger": "no ψ lifecycle" if status == "refused" else None,
            "replay_hash": "a" * 64 if status == "measured" else None,
        }
        rows[primitive] = row
    return {
        "version": "SEC-v3",
        "updated": "2026-11-19T00:00:00",
        "inventory": {
            "total": 4,
            "available": 3,
            "control_val_acc": 0.89,
            "bar": 0.106,
        },
        "base": {"task": "mnist", "batch_size": 32, "batch_limit": 375, "epochs": 1},
        "by_axis": {},
        "interaction": {
            "pair": ["credit", "dynamics"],
            "status": "measured",
            "levels": {"credit": ["gradient", "target_inversion"]},
            "control_val_acc": 0.89,
            "effect": {
                "effect": 0.0153,
                "lower": -0.0092,
                "upper": 0.0397,
                "seeds": 3,
            },
            "stop_reason": "rung 3",
        },
        "deep_dive": {
            "candidate": {
                "primitive": "primitive.credit_assignment.target_inversion",
                "axis": "credit",
                "level": "target_inversion",
                "val_acc": 0.1195,
                "margin": 0.0135,
                "knob": "credit.feedback_scale",
                "default": 0.01,
                "walltime_s": 1.0,
            },
            "ladder": [
                {
                    "factor": 0.1,
                    "value": 0.001,
                    "status": "measured",
                    "val_acc": 0.1195,
                    "walltime_s": 1.0,
                }
            ],
            "best": None,
            "cells": [],
            "effect": None,
            "claim": {
                "claim": "tuning the knob moves val_acc",
                "threshold": 0.01,
                "alpha": 0.05,
                "min_seeds": 5,
            },
            "verdict": "coordinate",
            "stop_reason": "the pair has no power",
            "walltime_s": 1.0,
            "knob_binds": False,
            "no_power": True,
        },
        "primitives": rows,
    }


def test_every_row_and_layer_appears(tmp_path: Path) -> None:
    data = _map()
    document = render_map(data)
    for primitive in data["primitives"]:
        assert primitive in document
    assert "credit × dynamics" in document
    assert "credit.feedback_scale" in document
    assert "knob binds: False; pair has power: False" in document
    assert "comp verify --primitive <id> --slice <family>" in document
    assert "param_count 999999 over ceiling" in document
    assert "no ψ lifecycle" in document
    assert document == render_map(data)

    map_path = tmp_path / "map.json"
    map_path.write_text(json.dumps(data))
    out = write_map_document(map_path, tmp_path / "docs" / "map.md")
    assert out.read_text() == document


def test_the_inventory_is_the_census_not_a_second_tally() -> None:
    document = render_map(_map())
    assert "**total 4** | 2 | 0 | 1 | 1 |" in document
    assert "| credit | 1 | 0 | 0 | 0 |" in document
