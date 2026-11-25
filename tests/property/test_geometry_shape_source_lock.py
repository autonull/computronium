"""Geometry spatial-fact lock (TODO104 A10, B5).

A geometry must read its extent from the task, never from an MNIST-shaped
default. Removing these refusals lets a cell train at a guessed 28x28 grid;
removing the guard must make this lock fail.
"""

from __future__ import annotations

import importlib
import inspect

import pytest
import torch


def _geometry_source() -> str:
    """The geometry module's source (``__import__`` returns the top package)."""
    module = importlib.import_module("computronium.ontology.geometry")
    return inspect.getsource(module)


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
    source = _geometry_source()
    for field in ("image_hw", "input_hw", "grid_hw", "lattice_dims"):
        assert f'getattr(config, "{field}"' not in source


def test_conv_pool_is_deterministic() -> None:
    """A divisible pool grid uses the operator with a deterministic backward.

    ``adaptive_avg_pool2d`` has no deterministic CUDA backward, so every conv
    cell at the reproducibility box died (TODO104 A15). The divisible case is
    the same pooling up to float summation order, and ``avg_pool2d`` is
    deterministic.
    """
    from computronium.ontology.geometry import _pool_to

    x = torch.arange(2 * 1 * 28 * 28, dtype=torch.float32).reshape(2, 1, 28, 28)
    pooled = _pool_to(x, (4, 4))
    reference = torch.nn.functional.avg_pool2d(x, (7, 7))
    assert pooled.shape == (2, 1, 4, 4)
    assert torch.allclose(pooled, reference)


def test_conv_reads_the_deterministic_pool() -> None:
    """The conv forward and its intermediates both route through ``_pool_to``."""
    source = _geometry_source()
    assert "adaptive_avg_pool2d(x, self.config.pool_hw)" not in source
    assert source.count("_pool_to(x, self.config.pool_hw)") == 2


def test_params_for_reads_the_tasks_extent() -> None:
    """A usps cell carries usps' grid, not its family base box's mnist grid."""
    from computronium.experiment.kernel.evaluate import task_shape
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _params_for

    axes = {**_AXIS_DEFAULTS, "geometry": "conv"}
    params = _params_for(axes, task_id="usps", shape=task_shape("usps", "cpu"))
    assert params["geometry.input_hw"] == (16, 16)
    assert params["geometry.in_channels"] == 1


def test_screen_coordinate_reads_its_box_task_extent() -> None:
    """The box builder carries the task's grid; the screen reads it back."""
    from computronium.experiment.sec_all_axes import _build_axis_box
    from computronium.experiment.sec_loop import screen_coordinate

    box = _build_axis_box("geometry", "conv", "usps")
    assert box["geometry.input_hw"] == (16, 16)

    coord = screen_coordinate(box, "geometry", "conv")
    assert coord.params["geometry.input_hw"] == (16, 16)
    assert coord.params["geometry.in_channels"] == 1


def test_a_lattice_box_carries_its_task_extent() -> None:
    """A lattice's (depth, height, width) is the 3-D task shape, not a literal."""
    from computronium.experiment.sec_all_axes import _build_axis_box

    box = _build_axis_box("geometry", "spatial_lattice", "mnist")

    assert box["geometry.lattice_dims"] == (1, 28, 28)


def test_a_graph_cell_is_legal_on_a_graph_task() -> None:
    """The evaluator composes with the task's edge_index; legality must too.

    Without the task instance the declared-space check refused every graph
    cell with "requires edge_index" while the evaluator would have supplied
    cora's own connectivity (TODO104 A30).
    """
    from computronium.experiment.kernel.evaluate import task_shape
    from computronium.experiment.sec_loop import _base_axes, _coordinate, _is_legal

    shape = task_shape("cora", "cpu")
    axes = _base_axes("cora")
    axes["geometry"] = "graph"
    coord = _coordinate(axes, task_id="cora", shape=shape)

    assert _is_legal(coord, "cora", shape) == (True, None)


def test_a_graph_cell_on_a_table_stays_refused() -> None:
    """A task without a graph is still refused by name, not admitted."""
    from computronium.experiment.kernel.evaluate import task_shape
    from computronium.experiment.sec_loop import _base_axes, _coordinate, _is_legal

    shape = task_shape("iris", "cpu")
    axes = _base_axes("iris")
    axes["geometry"] = "graph"
    coord = _coordinate(axes, task_id="iris", shape=shape)

    legal, reason = _is_legal(coord, "iris", shape)

    assert legal is False
    assert reason is not None


def test_params_for_carries_no_literal_extent() -> None:
    """The box builder has no MNIST-shaped fallback left to guess from."""
    from computronium.experiment.sec_loop import _params_for

    source = inspect.getsource(_params_for)
    assert "28, 28" not in source
    assert "16, 16" not in source


def test_own_knob_defaults_refuse_an_undeclared_extent() -> None:
    """A topology the task cannot declare has no invented structural default."""
    from computronium.experiment.sec_pilot import own_knob_params

    assert own_knob_params("geometry", "conv", "iris") == {}
    assert own_knob_params("geometry", "graph", "cora") == {}
    conv = own_knob_params("geometry", "conv", "usps")
    assert conv["geometry.input_hw"] == (16, 16)


def test_every_geometry_backend_builds() -> None:
    """The registry's conv entry builds a geometry, not the pool helper.

    A helper inserted between a ``@geometry_backend(...)`` decorator and its
    class registered the helper as the backend, and every conv cell died with
    ``_pool_to() missing 1 required positional argument`` (TODO104 A15).
    """
    from computronium.ontology.geometry import geometry_from_config

    config = GeometryConfig.conv(
        input_dim=784,
        output_dim=10,
        conv_channels=(4,),
        in_channels=1,
        input_hw=(28, 28),
        pool_hw=(4, 4),
    )
    geometry = geometry_from_config(config)
    assert type(geometry).__name__ == "ConvGeometry"
    out = geometry.forward(torch.randn(2, 784))
    assert out.shape == (2, 10)
