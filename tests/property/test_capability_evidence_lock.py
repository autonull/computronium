"""§2.1: a capability row is evidence only if its test exercises a mechanism.

Four rows of `CAPABILITIES` were marked complete on the strength of a name. The
locks here make the next one a test failure instead of a review question:

1. every active row names a verifying test that exists (D23: twenty-one rows
   named test files that had been deleted, so `comp conformance` could not have
   run them, and nineteen more named a function that does not exist);
2. every active row's test asserts — a test that only imports proves the name;
3. every CORE row reaches a kernel entry point with a call site outside its own
   module (§2.0: `__all__` membership is an offer, a call site is a use);
4. an UNVERIFIED row (D23's honest status) carries a reason, and the count is a
   ratchet so it cannot quietly rise;
5. the shape-only count is a ratchet, so the honest total cannot quietly rise.

Cost: tier 0. One AST read of the source tree, no training, no wall clock.
"""

from __future__ import annotations

import pytest

from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilityKind,
    CapabilityStatus,
)
from computronium.experiment.surface.evidence import (
    INDEX,
    SourceIndex,
    evidence_for,
)
from computronium.experiment.surface.evidence import _TestEvidence as TestEvidence

# Shape-only rows today: each names a test that asserts without calling a kernel
# entry point (an enum membership check, a protocol-shape declaration). They are
# enumerated in docs/generated/capabilities.md, not hidden.
SHAPE_ONLY_ALLOWANCE = 30


@pytest.fixture(scope="module")
def index() -> SourceIndex:
    return INDEX


@pytest.fixture(scope="module")
def verdicts() -> dict[str, TestEvidence]:
    return {
        capability_id: evidence_for(spec.verifying_test)
        for capability_id, spec in sorted(CAPABILITIES_REGISTRY.items())
    }


def _rows(status: CapabilityStatus = CapabilityStatus.ACTIVE) -> list[str]:
    return [
        capability_id
        for capability_id, spec in sorted(CAPABILITIES_REGISTRY.items())
        if spec.status == status
    ]


UNVERIFIED_ALLOWANCE = 21


def test_every_active_row_names_a_verifying_test() -> None:
    unnamed = [cap for cap in _rows() if not CAPABILITIES_REGISTRY[cap].verifying_test]
    assert unnamed == [], f"active capability without a verifying test: {unnamed}"


def test_every_verifying_test_exists(verdicts: dict[str, TestEvidence]) -> None:
    missing = [cap for cap in _rows() if not verdicts[cap].exists]
    assert missing == [], f"verifying test does not exist: {missing}"


def test_every_verifying_test_asserts(verdicts: dict[str, TestEvidence]) -> None:
    silent = [cap for cap in _rows() if not verdicts[cap].asserts]
    assert silent == [], f"verifying test asserts nothing: {silent}"


def test_every_core_row_has_mechanism_evidence(
    verdicts: dict[str, TestEvidence],
) -> None:
    shape = [
        cap
        for cap in _rows()
        if CAPABILITIES_REGISTRY[cap].kind is CapabilityKind.CORE
        and not verdicts[cap].mechanism
    ]
    assert shape == [], f"core capability proved by a name check only: {shape}"


def test_shape_only_rows_do_not_grow(verdicts: dict[str, TestEvidence]) -> None:
    shape = [cap for cap in _rows() if not verdicts[cap].mechanism]
    assert len(shape) <= SHAPE_ONLY_ALLOWANCE, (
        f"{len(shape)} rows are proved by a name check; "
        f"the honest allowance is {SHAPE_ONLY_ALLOWANCE}: {shape}"
    )


def test_an_unverified_row_records_its_reason() -> None:
    bare = [
        cap
        for cap in _rows(CapabilityStatus.UNVERIFIED)
        if not CAPABILITIES_REGISTRY[cap].unverified_reason
    ]
    assert bare == [], f"unverified capability without a reason: {bare}"


def test_unverified_rows_do_not_grow() -> None:
    unverified = _rows(CapabilityStatus.UNVERIFIED)
    assert len(unverified) <= UNVERIFIED_ALLOWANCE, (
        f"{len(unverified)} rows name no test that exists; "
        f"the honest allowance is {UNVERIFIED_ALLOWANCE}: {unverified}"
    )


def test_a_retired_row_records_its_reason() -> None:
    bare = [
        cap
        for cap in _rows(CapabilityStatus.RETIRED)
        if not CAPABILITIES_REGISTRY[cap].retirement_record
    ]
    assert bare == [], f"retired capability without a retirement record: {bare}"


def test_the_evidence_label_is_one_of_two_words(
    verdicts: dict[str, TestEvidence],
) -> None:
    assert {verdicts[cap].level for cap in _rows()} <= {"mechanism", "shape"}
