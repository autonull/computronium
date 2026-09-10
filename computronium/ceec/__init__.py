"""CEEC — Epistemic operating system for the Computronium Epistemic Foundry.

Implements CEEC-Core v1.0: immutable ledger, gated statuses, quarantine,
expected-value experiment selection, and calibration.
"""

from __future__ import annotations

from computronium.ceec import models
from computronium.ceec.ids import PREFIX_BY_KIND, prefix_for, validate_id
from computronium.ceec.store import CEECError, CEECStore, StoreError, now

__all__ = [
    "PREFIX_BY_KIND",
    "CEECError",
    "CEECStore",
    "StoreError",
    "models",
    "now",
    "prefix_for",
    "validate_id",
]
