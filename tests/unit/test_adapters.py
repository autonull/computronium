"""Adapter snapshot tests (GAME.todo7 §5.3) — lightweight, deterministic, no browser.

Parametrized over every registered adapter × real campaign root (populated +
empty, seeded by ``tests/ui/fixture.py``). Each adapter must return typed data
without I/O and be a pure function of its context: adapting the same context
twice yields equal dataclasses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from computronium.ui.adapters import ADAPTERS
from computronium.ui.data_adapters import AdapterContext
from computronium.visualization.live_atlas import (
    EmbedCache,
    _objectives_from_heartbeat,
    render_snapshot,
    resolve_log_path,
)
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path

ADAPTER_KEYS = sorted(ADAPTERS)


@pytest.fixture(scope="module")
def populated_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("adapters") / "broad_map"
    seed_campaign_root(root)
    return root


@pytest.fixture(scope="module")
def empty_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("adapters_empty") / "broad_map"
    root.mkdir(parents=True)
    return root


def _context(root: Path) -> AdapterContext:
    snapshot = render_snapshot(
        root,
        resolve_log_path(root, root / "logs" / "continuous_500.log"),
        EmbedCache(),
        objectives=_objectives_from_heartbeat(root),
        with_atlas=False,
    )
    return AdapterContext(root=root, snapshot=snapshot)


@pytest.mark.parametrize("adapter_key", ADAPTER_KEYS)
def test_adapter_returns_data_populated(adapter_key: str, populated_root: Path) -> None:
    """Every adapter handles the populated fixture root."""
    data = ADAPTERS[adapter_key].adapt(_context(populated_root))
    assert data is not None


@pytest.mark.parametrize("adapter_key", ADAPTER_KEYS)
def test_adapter_deterministic(adapter_key: str, populated_root: Path) -> None:
    """Adapting the same context twice yields equal data (purity lock)."""
    ctx = _context(populated_root)
    assert ADAPTERS[adapter_key].adapt(ctx) == ADAPTERS[adapter_key].adapt(ctx)


@pytest.mark.parametrize("adapter_key", ADAPTER_KEYS)
def test_adapter_empty_root(adapter_key: str, empty_root: Path) -> None:
    """Every adapter survives an empty root without raising."""
    data = ADAPTERS[adapter_key].adapt(_context(empty_root))
    assert data is not None


def test_registry_adapter_keys_resolve() -> None:
    """Every adapter_key referenced by views/tabs exists in ADAPTERS."""
    from computronium.ui.view_registry import registry

    missing = set()
    for view in registry._views.values():
        if view.adapter_key and view.adapter_key not in ADAPTERS:
            missing.add(view.adapter_key)
        for tab in view.tabs:
            if tab.adapter_key and tab.adapter_key not in ADAPTERS:
                missing.add(tab.adapter_key)
    for panel in registry._panels.values():
        if panel.adapter_key and panel.adapter_key not in ADAPTERS:
            missing.add(panel.adapter_key)
    assert not missing, f"unregistered adapter keys: {sorted(missing)}"
