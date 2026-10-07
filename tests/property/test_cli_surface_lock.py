"""F1 and F4: the command surface is locked, and a record says what it means.

Two claims, one selection, no cells.

**F1 — the surface is the product.** ``comp`` is the only entry point a user
types, so a command that exists in the dispatcher but is not in ``--help`` is a
command nobody can find, and a command in ``--help`` that the dispatcher refuses
is a promise the tool breaks. The list exists in exactly one place
(``_SUBCOMMANDS``), and this asserts the help text mirrors it in both
directions and that every entry is *reachable* — dispatched through the command
surface, not by calling a module's ``main`` directly.

Four commands had no test reaching them at all before this file (``parity``,
``repro``, ``validate``, ``joint-validate``): the surface lock stated a claim
about the surface that nothing executed.

Two ride-alongs from TODO48's opportunity 4:

* every ``POLICY_CATALOG`` entry is constructible from a spec alone, through the
  only path the command surface has — ``create_policy(name,
  **policy_context(spec, name))``. Two of eight were not, and no help-text lock
  could ever have found that.
* ``RecordSource`` — the slice of the store a policy reads — declared
  ``query_records(run_id, limit)`` positionally while ``RecordStore``'s is
  ``(run_id, *, …)``: a protocol no real store satisfies. The assertion is
  structural, because ``runtime_checkable`` only checks that the name exists.

**F4 — a record's procedure version is part of what it means.** The version was
the literal ``"1.0"`` at six call sites, and nothing could ask the store for the
records that predate a change. TODO48's own learning-rate fix is the case: a
pre-fix record measured a dead lr, and mixing it with post-fix records averages
two different experiments.
"""

from __future__ import annotations

import contextlib
import inspect
import io
from itertools import islice
from typing import TYPE_CHECKING

import pytest

from computronium.cli import __main__ as dispatcher
from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution import (
    POLICY_CATALOG,
    RecordSource,
    create_policy,
    iter_candidates,
    policy_context,
    search_space_from_spec,
    task_shape,
)
from computronium.experiment.schema.coordinate import Provenance
from computronium.experiment.schema.registries import (
    ASSESSMENT_PROCEDURE_VERSION,
    procedure_version_key,
)
from computronium.experiment.schema import seed_all_registries

from ._fake_backend import synthetic_record
from ._specs import mechanism_spec

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.record import Record

pytestmark = pytest.mark.timeout(300)

COMMANDS = tuple(sorted(dispatcher._SUBCOMMANDS))


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()


def _help(argv: list[str]) -> tuple[int, str]:
    """Run the command surface with stdout captured; return ``(code, text)``."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            code = dispatcher.main(argv)
        except SystemExit as exc:
            code = int(exc.code or 0)
    return code, buffer.getvalue()


class TestTheCommandSurface:
    def test_every_command_is_listed_in_help(self) -> None:
        assert COMMANDS, "the dispatcher declares no command"

        code, text = _help(["--help"])
        assert code == 0
        missing = [name for name in COMMANDS if name not in text]
        assert not missing, f"declared but absent from --help: {missing}"

    def test_every_command_in_help_is_declared(self) -> None:
        """The other direction: an advertised command the dispatcher refuses.

        Falsifiable by adding a row to ``_SUMMARIES`` alone — the help text is
        written from a second dict, so it can drift from the tree.
        """
        assert set(dispatcher._SUMMARIES) == set(dispatcher._SUBCOMMANDS), (
            "the summaries and the subcommands are two lists"
        )
        _code, text = _help(["--help"])
        for name in dispatcher._SUMMARIES:
            assert text.count(name) >= 1

    @pytest.mark.parametrize("command", COMMANDS)
    def test_every_command_is_reachable_through_the_surface(self, command: str) -> None:
        """Each command answers ``--help`` when typed, with no traceback.

        Falsifiable by breaking an adapter's parser: the dispatcher forwards the
        remainder unchanged, so a command whose adapter cannot parse ``--help``
        reaches the user as a crash on its own help text.
        """
        code, text = _help([command, "--help"])
        assert code == 0, f"comp {command} --help exited {code}"
        assert "usage:" in text.lower()

    def test_an_unknown_command_is_refused_without_a_traceback(self) -> None:
        code, text = _help(["not-a-command"])
        assert code == 2
        assert "Traceback" not in text

    def test_every_catalog_policy_is_constructible_from_a_spec_alone(self) -> None:
        """Opportunity 4: the catalog is only real if the surface can build it.

        Falsifiable by adding a row to ``POLICY_CATALOG`` with a required
        constructor argument ``policy_context`` does not supply — the shape two
        rows had, and the reason a help-text lock was not enough.
        """
        spec = mechanism_spec()
        for name in POLICY_CATALOG:
            policy = create_policy(name, **policy_context(spec, name, shape=task_shape))
            assert policy.get_name() or name

    def test_the_record_source_protocol_matches_the_real_store(self) -> None:
        """The protocol every policy is handed is one ``RecordStore`` satisfies.

        Falsifiable by making the protocol positional where the store is
        keyword-only: ``runtime_checkable`` still passes (the name is present),
        which is exactly how the mismatch survived.
        """
        protocol = inspect.signature(RecordSource.query_records)
        store = inspect.signature(RecordStore.query_records)
        # The protocol is the narrower declaration, so *it* is what the store
        # must satisfy: every parameter it names, the store accepts the same way.
        for name, declared in protocol.parameters.items():
            if name == "self":
                continue
            parameter = store.parameters.get(name)
            assert parameter is not None, f"the store cannot accept {name}"
            assert declared.kind is parameter.kind, (
                f"{name} is {declared.kind.name} on the protocol and "
                f"{parameter.kind.name} on the store"
            )


class TestAssessmentProcedureVersion:
    def _records(self, run_id: str) -> list[Record]:
        provenance = Provenance(
            env={},
            dataset="digits",
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={"run_id": run_id},
        )
        return [
            synthetic_record(
                coordinate,
                schedule,
                provenance,
                procedure_version=version,
            )
            for version, (coordinate, schedule) in zip(
                ("0.9", ASSESSMENT_PROCEDURE_VERSION),
                _first_two_cells(),
                strict=True,
            )
        ]

    def test_the_store_excludes_records_predating_a_procedure_change(
        self, tmp_path: Path
    ) -> None:
        """F4's gate: an old measurement is visible, and separable.

        Falsifiable by ignoring the filter — the store then returns both
        records, and a campaign that changed what a record means silently
        averages two experiments.
        """
        with RecordStore(StoreConfig(path=tmp_path / "versions.duckdb")) as store:
            run_id = store.create_run(spec=mechanism_spec())
            for record in self._records(run_id):
                store.append(record)
            everything = store.query_records(run_id=run_id)
            current = store.query_records(
                run_id=run_id,
                min_assessment_procedure_version=ASSESSMENT_PROCEDURE_VERSION,
            )

        versions = {r.status.assessment_procedure_version for r in everything}
        assert versions == {"0.9", ASSESSMENT_PROCEDURE_VERSION}
        assert len(everything) == 2
        assert [r.status.assessment_procedure_version for r in current] == [
            ASSESSMENT_PROCEDURE_VERSION
        ]

    def test_procedure_versions_order_numerically_not_lexically(self) -> None:
        """``1.10`` is newer than ``1.9`` — a string comparison says otherwise."""
        assert procedure_version_key("1.10") > procedure_version_key("1.9")
        assert procedure_version_key("2.0") > procedure_version_key("1.99")

    def test_an_unparseable_version_is_refused_rather_than_ordered(self) -> None:
        with pytest.raises(ValueError, match="assessment procedure version"):
            procedure_version_key("draft")


def _first_two_cells() -> list[tuple[Coordinate, Schedule]]:
    """Two cells of the shared declaration, as ``(coordinate, schedule)``."""
    spec = mechanism_spec()
    return list(
        islice(
            iter_candidates(
                spec,
                search_space_from_spec(spec, tasks=spec.task_names),
                shape=task_shape,
            ),
            2,
        )
    )
