"""T20.2.7 compat: standalone ceec matches the internal CEEC public API."""

from __future__ import annotations

import inspect

import ceec
import computronium.ceec as internal


def test_public_api_parity() -> None:
    # The standalone package adds the T20.2.3 constraint interface; the
    # internal surface must remain a subset of the standalone one.
    assert set(internal.__all__) <= set(ceec.__all__)


def test_store_surface_parity() -> None:
    external = {n for n in dir(ceec.CEECStore) if not n.startswith("_")}
    internal_surface = {n for n in dir(internal.CEECStore) if not n.startswith("_")}
    missing = external - internal_surface
    assert not missing, f"standalone CEECStore lost: {sorted(missing)}"


def test_record_evidence_signature_parity() -> None:
    internal_sig = inspect.signature(internal.CEECStore.record_evidence)
    external_sig = inspect.signature(ceec.CEECStore.record_evidence)
    assert internal_sig.parameters.keys() == external_sig.parameters.keys()


def test_cli_entrypoint_exists() -> None:
    from ceec.cli import main

    assert callable(main)
