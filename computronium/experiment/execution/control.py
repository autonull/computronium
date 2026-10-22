"""The control plane: one small document beside the store, both processes read and write (TODO70).

The dashboard's verbs must reach a run that lives in another process. The
event bus cannot carry them — it is process-local by construction
(``events.py``) — and the store cannot either: the dashboard refuses to write
it, and the run is the writer. So the control channel is a small JSON
document beside the store, and both sides derive its path from the store's by
one function, :func:`control_plane_path`. They cannot disagree about where it
lives because neither of them knows.

The document holds two sections:

``control``
    What the dashboard has asked the run to do — paused, a step owed, the
    ceiling on cells in flight, a request to stop. The dashboard writes it;
    the run reads it.

``status``
    What the run is doing now — the stage it is in, the cells in flight, the
    cells it has measured. The run writes it; the dashboard reads it.

A corrupt or half-written document is not an error. The plane reads as "not
paused" and records why it could not be read: a truncated file must not stop a
run, and a dashboard that cannot read the plane says so rather than showing a
control it cannot honour.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping

logger = logging.getLogger(__name__)

# The suffix the plane's document carries beside the store.
CONTROL_PLANE_SUFFIX: Final = ".control.json"

# How often a waiting run looks at the plane. The plane is a file: a run that
# holds at a boundary must notice a release promptly, and the cost of a look
# is one small read.
POLL_SECONDS: Final = 0.2

# The store name a pathless or in-memory store leaves the plane beside.
_DEFAULT_STORE_NAME: Final = "experiment"

_MEMORY_STORE: Final = ":memory:"

_CONTROL_FIELDS: Final = frozenset({"paused", "step_budget", "max_workers", "cancel"})


@dataclass(frozen=True, slots=True)
class ControlState:
    """What the dashboard has asked the run to do.

    Attributes:
        paused: Whether the run holds at its next boundary.
        step_budget: How many single batches the dashboard has released.
        max_workers: The ceiling on cells in flight, or ``None`` for the run's
            own.
        cancel: Whether the run has been asked to stop.
        revision: How many times the control section has been written. A
            browser that offers a stale revision is refused rather than
            applied.
        updated_at: When the control section was last written, in epoch
            seconds.
    """

    paused: bool = False
    step_budget: int = 0
    max_workers: int | None = None
    cancel: bool = False
    revision: int = 0
    updated_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """The section as it is written to the document."""
        return {
            "paused": self.paused,
            "step_budget": self.step_budget,
            "max_workers": self.max_workers,
            "cancel": self.cancel,
            "revision": self.revision,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ControlState:
        """A section as it is read from the document, missing fields and all.

        A document written by an older version of the dashboard names fewer
        fields; the ones it does not name keep their defaults rather than
        failing the read.
        """
        return cls(
            paused=bool(payload.get("paused", False)),
            step_budget=int(payload.get("step_budget", 0) or 0),
            max_workers=_optional_int(payload.get("max_workers")),
            cancel=bool(payload.get("cancel", False)),
            revision=int(payload.get("revision", 0) or 0),
            updated_at=float(payload.get("updated_at", 0.0) or 0.0),
        )


@dataclass(frozen=True, slots=True)
class RunStatus:
    """What the run is doing now, for the dashboard to read.

    Attributes:
        run_id: The run these counters belong to.
        stage: The stage the run is in, by its own name.
        in_flight: The cells training right now.
        cells_done: The cells the run has measured.
        ceiling: The ceiling on cells in flight the run is holding to.
        at: When the run last said so, in epoch seconds.
    """

    run_id: str = ""
    stage: str = ""
    in_flight: int = 0
    cells_done: int = 0
    ceiling: int = 0
    at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """The section as it is written to the document."""
        return {
            "run_id": self.run_id,
            "stage": self.stage,
            "in_flight": self.in_flight,
            "cells_done": self.cells_done,
            "ceiling": self.ceiling,
            "at": self.at,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> RunStatus:
        """A section as it is read from the document."""
        return cls(
            run_id=str(payload.get("run_id", "")),
            stage=str(payload.get("stage", "")),
            in_flight=int(payload.get("in_flight", 0) or 0),
            cells_done=int(payload.get("cells_done", 0) or 0),
            ceiling=int(payload.get("ceiling", 0) or 0),
            at=float(payload.get("at", 0.0) or 0.0),
        )


def _optional_int(value: object) -> int | None:
    """An optional integer, read from a document that may hold anything."""
    if value is None:
        return None
    try:
        return int(value)  # type: ignore[call-overload]
    except TypeError, ValueError:
        return None


def control_plane_path(store_path: str | Path | None) -> Path:
    """The plane's path, derived from the store's.

    The only place that knows where the control channel lives: the dashboard
    and the run both call this, so they cannot look in different places. A
    store with no path — an in-memory one, or none at all — puts the plane
    beside the working directory, where it is still one path for both sides.

    Args:
        store_path: The store's path, as the dashboard and the CLI were given
            it.

    Returns:
        The path of the control document.
    """
    if store_path is None:
        return Path.cwd() / f"{_DEFAULT_STORE_NAME}{CONTROL_PLANE_SUFFIX}"
    text = str(store_path)
    if not text or text == _MEMORY_STORE:
        return Path.cwd() / f"{_DEFAULT_STORE_NAME}{CONTROL_PLANE_SUFFIX}"
    path = Path(text)
    if path.suffix:
        return path.with_suffix(CONTROL_PLANE_SUFFIX)
    return path.with_name(f"{path.name}{CONTROL_PLANE_SUFFIX}")


class ControlPlane:
    """The document the dashboard writes and the run reads.

    Both halves of the document are written whole, each preserving the other
    half, so a control write never drops the run's status and a status write
    never drops a pause. The rewrite is guarded by an advisory lock on a file
    beside the document: without it, a pause written at the same moment as a
    status update can be lost, and a lost pause is a control that does not
    work.
    """

    def __init__(self, path: str | Path) -> None:
        """Bind the plane to its document.

        Args:
            path: The document's path, from :func:`control_plane_path`.
        """
        self.path = Path(path)
        self.last_error: str | None = None

    def read(self) -> ControlState:
        """The control section, as it stands.

        A document that cannot be read is not an error the caller must
        handle: the plane reads as "not paused", and ``last_error`` says why.
        """
        document = self._load()
        return ControlState.from_dict(document.get("control", {}))

    def read_status(self) -> RunStatus | None:
        """The run's status, or ``None`` when the run has not written any."""
        document = self._load()
        section = document.get("status")
        if not isinstance(section, dict):
            return None
        return RunStatus.from_dict(section)

    def read_all(self) -> tuple[ControlState, RunStatus | None]:
        """Both halves of the document, read once.

        The dashboard polls at 2 Hz: reading the document twice for the two
        halves would be two reads of the same bytes.
        """
        document = self._load()
        section = document.get("status")
        status = RunStatus.from_dict(section) if isinstance(section, dict) else None
        return ControlState.from_dict(document.get("control", {})), status

    def write(self, **changes: bool | int | None) -> ControlState:
        """Merge changes into the control section and return the new state.

        Args:
            changes: The fields to change. ``paused``, ``max_workers`` and
                ``cancel`` are set; ``step=True`` releases one more batch.

        Returns:
            The control section as it now stands.

        Raises:
            ValueError: If a change names a field the plane does not have.
        """
        unknown = set(changes) - _CONTROL_FIELDS - {"step"}
        if unknown:
            msg = f"unknown control field(s): {sorted(unknown)}"
            raise ValueError(msg)

        with self._locked():
            document = self._load()
            current = ControlState.from_dict(document.get("control", {}))
            updates: dict[str, Any] = {}
            for key, value in changes.items():
                if key == "step":
                    if value:
                        updates["step_budget"] = current.step_budget + 1
                    continue
                if key == "max_workers":
                    updates[key] = _optional_int(value)
                    continue
                if key == "step_budget":
                    updates[key] = int(value or 0)
                    continue
                updates[key] = bool(value)
            merged = replace(
                current,
                **updates,
                revision=current.revision + 1,
                updated_at=time.time(),
            )
            document["control"] = merged.to_dict()
            self._persist(document)
            return merged

    def write_status(self, status: RunStatus) -> None:
        """Publish what the run is doing now.

        A failure to publish is logged and dropped: the run's own work does
        not depend on the dashboard reading it.
        """
        try:
            with self._locked():
                document = self._load()
                document["status"] = status.to_dict()
                self._persist(document)
        except OSError as exc:
            logger.debug("Could not publish the run's status: %s", exc)

    async def wait_for_release(
        self,
        *,
        steps_taken: int = 0,
        poll: float = POLL_SECONDS,
    ) -> ControlState:
        """Wait until the plane releases the run.

        The run is released when the plane is not paused, when it has been
        asked to stop, or when a step is owed — the dashboard has released
        more batches than the run has taken.

        Args:
            steps_taken: How many single batches the run has already taken.
            poll: How long to wait between looks at the plane.

        Returns:
            The control section that released the run.
        """
        while True:
            state = self.read()
            if state.cancel:
                return state
            if not state.paused:
                return state
            if state.step_budget > steps_taken:
                return state
            await asyncio.sleep(poll)

    def _load(self) -> dict[str, Any]:
        """The document, or an empty one when it cannot be read."""
        try:
            raw = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.last_error = None
            return {}
        except OSError as exc:
            self.last_error = str(exc)
            return {}
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.last_error = f"the control plane could not be read: {exc}"
            return {}
        if not isinstance(document, dict):
            self.last_error = "the control plane is not a document"
            return {}
        self.last_error = None
        return document

    def _persist(self, document: dict[str, Any]) -> None:
        """Replace the document atomically, so a reader never sees a half one."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(document, indent=2, sort_keys=True)
        temporary = self.path.with_name(f"{self.path.name}.{os.getpid()}.tmp")
        try:
            temporary.write_text(payload, encoding="utf-8")
            temporary.replace(self.path)
        except BaseException:
            with contextlib.suppress(OSError):
                temporary.unlink()
            raise

    @contextlib.contextmanager
    def _locked(self) -> Generator[None]:
        """Hold the plane's lock while the document is read and rewritten."""
        try:
            import fcntl
        except ImportError:  # pragma: no cover - Windows has no fcntl
            yield
            return
        lock_path = self.path.with_name(f"{self.path.name}.lock")
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            handle = lock_path.open("a+")
        except OSError:
            yield
            return
        with handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


__all__ = [
    "CONTROL_PLANE_SUFFIX",
    "POLL_SECONDS",
    "ControlPlane",
    "ControlState",
    "RunStatus",
    "control_plane_path",
]
