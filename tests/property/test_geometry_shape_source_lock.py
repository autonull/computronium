"""Geometry spatial-fact lock (TODO104 A10, B5).

A geometry must read its extent from the task, never from an MNIST-shaped
default. Removing these refusals lets a cell train at a guessed 28x28 grid;
removing the guard must make this lock fail.
"""

from __future__ import annotations

import inspect

import pytest

from computronium.experiment.kernel._geometry_builders import (
    build_graph_config,
    build_spatial_lattice_config,
)
from computronium.ontology.geometry import GeometryConfig


def test_spatial_lattice_requires_an_extent() -> None:
    """A lattice cell that declares no extent is refused by name."""
    with pytest.raises(ValueError, match="lattice_dims"):
        build_spatial_lattice_config(
            input_dim=64,
            output_dim=10,
            param_budget=0,
            hidden=32,
            depth=2,
            init_scale=0.1,
            geometry={},
        )


def test_graph_requires_its_connectivity() -> None:
    """A graph cell that declares no edge_index is refused by name."""
    with pytest.raises(ValueError, match="edge_index"):
        build_graph_config(
            input_dim=32,
            output_dim=10,
            hidden=16,
            depth=2,
            init_scale=0.1,
            init_scheme="default",
            geometry={},
        )


def test_spatial_lattice_factory_has_no_default_extent() -> None:
    """The factory cannot invent a lattice extent."""
    parameter = inspect.signature(GeometryConfig.spatial_lattice).parameters[
        "lattice_dims"
    ]
    assert parameter.default is inspect.Parameter.empty


def test_geometry_reads_no_getattr_extent() -> None:
    """An extent field is read directly, so a missing one fails loud."""
    source = inspect.getsource(__import__("computronium.ontology.geometry"))
    for field in ("image_hw", "input_hw", "grid_hw", "lattice_dims"):
        assert f'getattr(config, "{field}"' not in source
