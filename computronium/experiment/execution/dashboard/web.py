"""Web Dashboard for Live Campaign Monitoring (Phase E5).

FastAPI-based web dashboard with three.js frontend for real-time updates.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import math
import os
import shutil
import tempfile
import uuid
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

from computronium.experiment.evidence.serializers import serializer
from computronium.experiment.execution.control import ControlPlane, control_plane_path
from computronium.experiment.execution.dashboard.actions import (
    KIND_CONFIRMATION,
    KIND_QUEST,
    ActionUnavailableError,
    CellTarget,
    cell_evidence,
    cell_spec,
    claim_sentence,
    default_metric,
    measurement_budget,
    records_for_cell,
    registration_name,
    registration_payload,
    run_spread,
    write_registration,
)
from computronium.experiment.execution.dashboard.multirun import (
    SpaceReader,
    multirun_payload,
)
from computronium.experiment.execution.dashboard.narration import (
    Narration,
    state_sentences,
)
from computronium.experiment.execution.dashboard.runs import (
    DEFAULT_STORE,
    axes_payload,
    profiles_payload,
)
from computronium.experiment.execution.events import (
    PipelineEvent,
    get_event_bus,
    publish_event,
)
from computronium.experiment.schema.axis import StructuralAxis

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Sequence

    from computronium.experiment.evidence.mirror import StoreView
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.campaign_queue import (
        CampaignQueue,
    )
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec
    from computronium.experiment.surface.report import CellKey

logger = logging.getLogger(__name__)

# Pareto objectives: maximize task accuracy, minimize wall cost.
PARETO_OBJECTIVES = ("validation_accuracy", "walltime_total")


class CellAction(BaseModel):
    """What the dashboard asks for when it acts on a cell."""

    model_config = ConfigDict(extra="forbid")

    coordinate: dict[str, str]
    seeds: int | None = Field(default=None, gt=0)
    threshold: float | None = None
    alpha: float | None = Field(default=None, gt=0.0, lt=1.0)
    min_seeds: int | None = Field(default=None, gt=0)


class SpaceRequest(BaseModel):
    """Which axes the grid shows."""

    model_config = ConfigDict(extra="forbid")

    axes: list[str] = Field(
        default_factory=lambda: ["credit", "geometry", "dynamics"],
        min_length=3,
        max_length=3,
    )


class ControlCommand(BaseModel):
    """What the dashboard asks the run to do.

    Every field is optional: a command names only the verb it means. The
    revision is the one the browser last saw, so a write from a stale page is
    refused rather than applied.
    """

    model_config = ConfigDict(extra="forbid")

    paused: bool | None = None
    step: bool | None = None
    max_workers: int | None = Field(default=None, gt=0)
    cancel: bool | None = None
    revision: int | None = Field(default=None, ge=0)


class RunRequest(BaseModel):
    """The run the reader asked for."""

    model_config = ConfigDict(extra="forbid")

    profile: str
    overrides: dict[str, Any] = Field(default_factory=dict)
    device: str | None = None


class _CpuSampler:
    """The machine's CPU use, sampled without blocking.

    ``psutil``'s non-blocking percentage compares this call with the last
    one, so the first sample has nothing to compare and reads zero. The
    sampler keeps the last reading and hands it out again until a second
    sample exists, so a reader never sees a machine that looks idle because
    the page had just opened.
    """

    def __init__(self) -> None:
        self._last = 0.0
        self._primed = False

    def read(self) -> float:
        """The machine's CPU use, as a percentage."""
        try:
            import psutil
        except ImportError:
            return self._last
        sample = psutil.cpu_percent(interval=None)
        if self._primed:
            self._last = sample
        else:
            self._primed = True
        return self._last


def resolve_axes(names: Sequence[str]) -> list[StructuralAxis]:
    """The three axes a picture shows.

    Args:
        names: The axes the reader asked for.

    Returns:
        The axes, in the order they were asked for.

    Raises:
        ValueError: The request does not name three different axes.
    """
    axes: list[StructuralAxis] = []
    for name in names:
        try:
            axes.append(StructuralAxis(name))
        except ValueError as exc:
            raise ValueError(f"unknown axis: {name}") from exc
    if len(set(axes)) != len(axes):
        raise ValueError("the grid shows three different axes")
    return axes


@dataclass(frozen=True, slots=True)
class ActionResult:
    """What an action did."""

    payload: dict[str, Any]
    status_code: int = 200


@dataclass(frozen=True, slots=True)
class CellContext:
    """Everything an action needs to know about one cell."""

    source: RunSpec
    target: CellTarget
    records: list[Record]
    run_records: list[Record]
    metric: str
    task_id: str
    chance: float | None
    required_seeds: int
    alpha: float


def declared_cells(spec: RunSpec | None) -> int:
    """How many cells the run's own declaration holds.

    The axes the run does not narrow permit everything on them, so a run
    that declares nothing declares the whole space.
    """
    if spec is None:
        return 0
    return math.prod(len(spec.selected_primitives(axis)) for axis in StructuralAxis)


def run_status(
    spec: RunSpec | None,
    run_id: str,
    claim_metrics: tuple[str, ...] = (),
    started_at: datetime | None = None,
    cells: frozenset[CellKey] = frozenset(),
    status: str | None = None,
) -> dict[str, Any]:
    """What the run declares, and whether its claim is preregistered.

    A metric carrying a threshold in ``configs/preregistrations/`` is a
    confirmatory one; every other claim is exploratory. The dashboard reports
    which, rather than asserting a status the run never declared. Only a
    threshold written before the run began counts: one written afterwards was
    written with the run's own data in hand. Only a threshold about a cell
    the run measured counts: one about another cell says nothing about this
    run's claims.
    """
    from computronium.experiment.surface.report import preregistered_metrics

    registered = preregistered_metrics(started_at, cells)
    mode = (
        "PREREGISTERED"
        if claim_metrics and all(metric in registered for metric in claim_metrics)
        else "EXPLORATORY"
    )

    return {
        "run_id": run_id,
        "profile": spec.profile if spec else None,
        "tasks": list(spec.task_names) if spec else [],
        "fidelity": spec.fidelity if spec else None,
        "objectives": list(spec.objectives) if spec else [],
        "claim_metrics": list(claim_metrics),
        "mode": mode,
        "status": status,
        "declared_cells": declared_cells(spec),
        "started_at": started_at.isoformat() if started_at else None,
    }


@dataclass(frozen=True, slots=True)
class DashboardConfig:
    """Configuration for the web dashboard.

    The dashboard never writes to the store: it reads the store when it can
    and the writer's published mirror when the writer is elsewhere.
    """

    host: str = "0.0.0.0"
    port: int = 8080
    update_interval: float = 2.0  # seconds
    store_path: str | None = None
    campaign_queue: CampaignQueue | None = None
    enable_websockets: bool = True
    template_dir: Path | None = None
    static_dir: Path | None = None
    registration_dir: Path | None = None  # where the dashboard writes registrations


class WebDashboard:
    """Web-based live monitoring dashboard.

    Provides real-time visibility into:
    - Campaign queue status (queued, running, completed)
    - Resource utilization (GPU, CPU, memory)
    - Individual campaign progress
    - Metrics streaming from running experiments
    - Cost tracking (GPU-hours, energy, carbon)
    """

    def __init__(self, config: DashboardConfig | None = None) -> None:
        # The registries seed themselves on first use, and that seeding is
        # not re-entrant: two requests arriving together would each try to
        # seed them, and the second would find them half-built — a profile
        # whose axes name no primitive. The dashboard seeds them once, here,
        # before it serves anything.
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()
        self.config = config or DashboardConfig()
        self.app = FastAPI(
            title="Computronium Campaign Dashboard", lifespan=self._lifespan
        )
        self._connected_websockets: set[WebSocket] = set()
        self._ws_locks: dict[WebSocket, asyncio.Lock] = {}
        self._running = False
        self._update_task: asyncio.Task | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._unsubscribe: Callable[[], None] | None = None
        self._run_record_counts: dict[str, int] = {}
        self._reported_runs: set[str] = set()
        self._event_history: deque[dict[str, Any]] = deque(maxlen=200)
        self._narration = Narration()
        self._dynamics_cache: dict[str, dict[str, Any]] = {}
        self._space_reader = SpaceReader()
        self._work_dir: Path | None = None
        # The channel to the run: the same document the run reads, derived
        # from the same store path (TODO70).
        self._control = ControlPlane(control_plane_path(self.config.store_path))
        self._cpu = _CpuSampler()
        # Server-side metrics cache: key = (run_id, record_count, status)
        # Value = detailed metrics. Finished runs are immutable; only running
        # runs with changing record counts are recomputed.
        self._metrics_cache: dict[tuple[str, int, str], dict[str, Any]] = {}
        self._setup_routes()
        self._setup_templates()

    @contextlib.asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        """Lifespan handler to start/stop the dashboard update loop."""
        await self.start()
        try:
            yield
        finally:
            await self.stop()

    def _setup_templates(self) -> None:
        """Setup Jinja2 templates."""
        template_dir = self.config.template_dir or Path(__file__).parent / "templates"
        self.templates = Jinja2Templates(directory=str(template_dir))

        static_dir = (
            self.config.static_dir or Path(__file__).parent / "templates" / "static"
        )
        if static_dir.exists():
            self.app.mount(
                "/static", StaticFiles(directory=str(static_dir)), name="static"
            )

    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""

        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request) -> HTMLResponse:
            return self.templates.TemplateResponse(request=request, name="index.html")

        @self.app.get("/api/status")
        async def api_status() -> JSONResponse:
            return JSONResponse(await self._get_status())

        @self.app.get("/api/queue")
        async def api_queue() -> JSONResponse:
            return JSONResponse(await self._get_queue_status())

        @self.app.get("/api/narration")
        async def api_narration(run_id: str | None = None) -> JSONResponse:
            """What the dashboard is doing, in words (TODO69).

            The same sentences the browser renders as captions, so an agent
            can read the screen's story without a browser.
            """
            return JSONResponse(await self._narration_payload(run_id))

        @self.app.get("/api/events")
        def api_events(run_id: str | None = None) -> JSONResponse:
            """The run's stages, as they happened (TODO69).

            The events are process-local, so this is the run *this dashboard
            watched* — and a run that happened elsewhere has no timeline here.
            """
            return JSONResponse(self._event_payload(run_id))

        @self.app.get("/api/runs/{run_id}/account")
        async def api_run_account(run_id: str) -> JSONResponse:
            """The run's account of itself (TODO69).

            The ledger is what the run can say — its claims, the gate's
            verdicts, the limitations that hold it back. The contrast is its
            arms against one another, with the test it could or could not run.
            """
            return JSONResponse(await self._account_payload(run_id))

        @self.app.get("/api/runs/{run_id}/flow")
        async def api_run_flow(run_id: str) -> JSONResponse:
            """The run's cells, from the space to the evidence (TODO69).

            The stages the run reached, the counts each one reported, and
            what the gate refused: the run as a process, read from the
            events this dashboard watched.
            """
            return JSONResponse(self._flow_payload(run_id))

        @self.app.get("/api/runs/{run_id}/attribution")
        async def api_run_attribution(run_id: str) -> JSONResponse:
            """What the run can attribute, and what it cannot (TODO69).

            The axes that varied, how far apart their arms stand, and the
            axes that were held fixed — which is what a run's design cannot
            speak about, and says so.
            """
            return JSONResponse(await self._attribution_payload(run_id))

        @self.app.get("/api/runs/{run_id}/dynamics")
        async def api_run_dynamics(run_id: str) -> JSONResponse:
            """The cell's own dynamics, measured (TODO69).

            Where the state goes, whether it settles, how much of the
            neighbourhood comes back, and what its energy looks like over
            the slice its own trajectory crosses.
            """
            return JSONResponse(await self._dynamics_payload(run_id))

        @self.app.get("/api/cells/dynamics")
        async def api_cell_dynamics(
            substrate: str,
            geometry: str,
            dynamics: str,
            plasticity: str,
            credit: str,
            update: str,
            task: str = "digits",
        ) -> JSONResponse:
            """One cell's own dynamics, measured (TODO69).

            The endpoint is asked for a *cell*, not a run: the run's own
            cells are usually feedforward with an instantaneous pass, and
            such a cell has no state that moves.
            """
            from computronium.experiment.execution.dashboard.dynamics import (
                measure_cell,
            )

            values = {
                "substrate": substrate,
                "geometry": geometry,
                "dynamics": dynamics,
                "plasticity": plasticity,
                "credit": credit,
                "update": update,
            }
            try:
                measured = await asyncio.to_thread(measure_cell, values, task)
                return JSONResponse(measured)
            except Exception as e:
                logger.exception("Error measuring the cell's dynamics")
                return JSONResponse({"error": str(e)}, status_code=409)

        @self.app.get("/api/runs/{run_id}/dynamics/trained")
        async def api_run_trained_dynamics(run_id: str) -> JSONResponse:
            """The run's cell, trained first, then its dynamics measured (TODO69).

            A trained cell settles where an untrained one does not. The
            training is expensive, so the result is cached.
            """
            return JSONResponse(await self._trained_dynamics_payload(run_id))

        @self.app.get("/api/cells/dynamics/trained")
        async def api_cell_trained_dynamics(
            substrate: str,
            geometry: str,
            dynamics: str,
            plasticity: str,
            credit: str,
            update: str,
            task: str = "digits",
            epochs: int = 10,
        ) -> JSONResponse:
            """One cell's dynamics after training, measured (TODO69).

            The cell is trained for the given epochs, then its relaxation is
            measured. This is the picture a trained cell shows.
            """
            from computronium.experiment.execution.dashboard.dynamics import (
                _train_and_measure_cell,
            )

            values = {
                "substrate": substrate,
                "geometry": geometry,
                "dynamics": dynamics,
                "plasticity": plasticity,
                "credit": credit,
                "update": update,
            }
            try:
                measured = await asyncio.to_thread(
                    _train_and_measure_cell, values, task, epochs=epochs
                )
                return JSONResponse(measured)
            except Exception as e:
                logger.exception("Error measuring the trained cell's dynamics")
                return JSONResponse({"error": str(e)}, status_code=409)

        @self.app.get("/api/resources")
        async def api_resources() -> JSONResponse:
            return JSONResponse(await self._get_resource_usage())

        @self.app.get("/api/campaigns")
        async def api_campaigns() -> JSONResponse:
            return JSONResponse(await self._get_all_campaigns())

        @self.app.get("/api/runs")
        async def api_runs() -> JSONResponse:
            return JSONResponse(await self._get_store_runs())

        @self.app.get("/api/campaigns/{campaign_id}")
        async def api_campaign_detail(campaign_id: str) -> JSONResponse:
            return JSONResponse(await self._get_campaign_detail(campaign_id))

        @self.app.get("/api/campaigns/{campaign_id}/metrics")
        async def api_campaign_metrics_detailed(campaign_id: str) -> JSONResponse:
            return JSONResponse(await self._get_campaign_metrics_detailed(campaign_id))

        @self.app.get("/api/metrics/{campaign_id}")
        async def api_campaign_metrics_legacy(campaign_id: str) -> JSONResponse:
            return JSONResponse(await self._get_campaign_metrics(campaign_id))

        @self.app.get("/api/cost/{campaign_id}")
        async def api_campaign_cost(campaign_id: str) -> JSONResponse:
            return JSONResponse(await self._get_campaign_cost(campaign_id))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket) -> None:
            await self._handle_websocket(websocket)

        @self.app.post("/api/campaigns/{campaign_id}/cancel")
        async def api_cancel_campaign(campaign_id: str) -> JSONResponse:
            if self.config.campaign_queue:
                success = await self.config.campaign_queue.cancel(campaign_id)
                return JSONResponse({"success": success})
            return JSONResponse({
                "success": False,
                "error": "No campaign queue configured",
            })

        @self.app.post("/api/campaigns/{campaign_id}/preempt")
        async def api_preempt_campaign(campaign_id: str) -> JSONResponse:
            if self.config.campaign_queue:
                success = await self.config.campaign_queue.preempt(campaign_id)
                return JSONResponse({"success": success})
            return JSONResponse({
                "success": False,
                "error": "No campaign queue configured",
            })

        @self.app.post("/api/cells/{run_id}/replicate")
        async def api_replicate_cell(
            run_id: str,
            body: CellAction,
        ) -> JSONResponse:
            result = await self._replicate_cell(run_id, body)
            return JSONResponse(result.payload, status_code=result.status_code)

        @self.app.post("/api/cells/{run_id}/preregister")
        async def api_preregister_cell(
            run_id: str,
            body: CellAction,
        ) -> JSONResponse:
            result = await self._preregister_cell(run_id, body)
            return JSONResponse(result.payload, status_code=result.status_code)

        @self.app.post("/api/cells/{run_id}/quest")
        async def api_adopt_quest(
            run_id: str,
            body: CellAction,
        ) -> JSONResponse:
            result = await self._adopt_quest(run_id, body)
            return JSONResponse(result.payload, status_code=result.status_code)

        @self.app.post("/api/cells/{run_id}/space")
        async def api_cell_space(
            run_id: str,
            body: SpaceRequest,
        ) -> JSONResponse:
            result = await self._cell_space(run_id, body)
            return JSONResponse(result.payload, status_code=result.status_code)

        @self.app.post("/api/spaces")
        async def api_spaces(body: SpaceRequest) -> JSONResponse:
            """Several runs' evidence in one space (TODO69).

            The runs of the store, each in its own window on the same
            declared space, with the cells each of them measured.
            """
            return JSONResponse(await self._spaces_payload(body))

        @self.app.get("/api/control")
        async def api_control() -> JSONResponse:
            """The control plane, the run's counters, and the machine's use.

            The control bar polls this at 2 Hz, so every part of it is cheap:
            the plane is a small document, the run's counters come from the
            same document, and the machine's CPU is a non-blocking sample.
            """
            return JSONResponse(await self._control_payload())

        @self.app.post("/api/control")
        async def api_control_command(body: ControlCommand) -> JSONResponse:
            """Ask the run to do something.

            The command merges into the plane. A browser that offers a stale
            revision is refused rather than applied: two pages driving one
            run must not overwrite each other.
            """
            result = await self._apply_control(body)
            return JSONResponse(result.payload, status_code=result.status_code)

        @self.app.get("/api/profiles")
        def api_profiles() -> JSONResponse:
            """The run profiles, as data: what the new-run form offers."""
            return JSONResponse(profiles_payload())

        @self.app.get("/api/axes")
        def api_axes() -> JSONResponse:
            """The six structural axes and the primitives each one offers."""
            return JSONResponse(axes_payload())

        @self.app.get("/api/databases")
        async def api_databases() -> JSONResponse:
            """List available databases."""
            from pathlib import Path

            databases = []
            seen_paths = set()
            # Look for .duckdb files in common locations
            search_paths = [
                Path.cwd(),
                Path.cwd() / "experiments",
                Path.home() / "computronium",
            ]

            for search_path in search_paths:
                if search_path.exists():
                    for db_file in search_path.glob("*.duckdb"):
                        try:
                            resolved = db_file.resolve()
                            if resolved in seen_paths:
                                continue
                            seen_paths.add(resolved)
                            stat = resolved.stat()
                            # Count runs in this database
                            runs = 0
                            try:
                                from computronium.experiment.evidence.store import (
                                    RecordStore,
                                    StoreConfig,
                                )

                                with RecordStore(
                                    StoreConfig(path=resolved, read_only=True)
                                ) as store:
                                    runs = len(list(store.query_runs()))
                            except Exception:
                                pass

                            databases.append({
                                "path": str(resolved),
                                "name": resolved.name,
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(
                                    stat.st_mtime
                                ).isoformat(),
                                "runs": runs,
                            })
                        except Exception:
                            pass

            # Also check the configured store
            current_path = self.config.store_path or "experiment.duckdb"
            current_found = any(db["path"] == current_path for db in databases)

            return JSONResponse({
                "databases": databases,
                "current": current_path
                if current_found
                else (databases[0]["path"] if databases else current_path),
            })

        @self.app.post("/api/databases/create")
        async def api_create_database(request: Request) -> JSONResponse:
            """Create a new database."""
            from pathlib import Path

            from computronium.experiment.evidence.store import RecordStore, StoreConfig

            body = await request.json()
            name = body.get("name", "experiment")
            path = body.get("path", f"{name}.duckdb")

            db_path = Path(path)
            if not db_path.is_absolute():
                db_path = Path.cwd() / db_path

            # Ensure parent directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)

            if db_path.exists():
                return JSONResponse(
                    {"error": "Database already exists"}, status_code=409
                )

            # Create the database by initializing a store
            try:
                with RecordStore(StoreConfig(path=db_path, read_only=False)) as store:
                    # Just opening it creates the schema
                    pass
            except Exception as e:
                return JSONResponse({"error": str(e)}, status_code=500)

            return JSONResponse({"path": str(db_path), "name": name})

        @self.app.post("/api/databases/switch")
        async def api_switch_database(request: Request) -> JSONResponse:
            """Switch the active database (requires restart)."""
            body = await request.json()
            path = body.get("path")
            if not path:
                return JSONResponse({"error": "No path provided"}, status_code=400)

            # The dashboard needs to restart to use the new database
            # We just validate it exists and return success
            db_path = Path(path)
            if not db_path.exists():
                return JSONResponse({"error": "Database not found"}, status_code=404)

            return JSONResponse({
                "success": True,
                "path": str(db_path),
                "message": "Database switched. Dashboard will reload.",
            })

        @self.app.get("/api/databases/export")
        async def api_export_database(path: str) -> JSONResponse:
            """Export database as download."""
            from pathlib import Path

            from fastapi.responses import FileResponse

            db_path = Path(path)
            if not db_path.exists():
                return JSONResponse({"error": "Database not found"}, status_code=404)

            return FileResponse(
                path=db_path,
                filename=db_path.name,
                media_type="application/octet-stream",
            )

        @self.app.post("/api/databases/import")
        async def api_import_database(request: Request) -> JSONResponse:
            """Import database from uploaded file."""
            from pathlib import Path

            form = await request.form()
            file = form.get("file")
            if not file or not hasattr(file, "filename"):
                return JSONResponse({"error": "No file uploaded"}, status_code=400)

            filename = file.filename or "imported.duckdb"
            dest_path = Path.cwd() / filename

            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = Path(filename).stem
                suffix = Path(filename).suffix
                dest_path = Path.cwd() / f"{stem}-{counter}{suffix}"
                counter += 1

            try:
                with Path(dest_path).open("wb") as f:
                    content = await file.read()
                    f.write(content)
            except Exception as e:
                return JSONResponse({"error": str(e)}, status_code=500)

            return JSONResponse({"path": str(dest_path), "name": dest_path.name})

        @self.app.get("/api/runs/{run_id}/records")
        async def api_run_records(run_id: str) -> JSONResponse:
            """The run's records, as JSON.

            The export a reader takes away: the run's own evidence, in the
            form the store holds it.
            """
            return JSONResponse(await self._records_payload(run_id))

        @self.app.get("/api/runs/{run_id}/report")
        async def api_run_report(run_id: str) -> JSONResponse:
            """The run's report, as the terminal shows it.

            The dashboard's own account of the run, in the run's own words.
            """
            return JSONResponse(await self._report_payload(run_id))

        @self.app.post("/api/runs")
        async def api_start_run(body: RunRequest) -> JSONResponse:
            """Start a run from the dashboard.

            Without a campaign queue the answer is the command to type: the
            dashboard must never appear to have a control it does not have.
            """
            result = await self._start_run(body)
            return JSONResponse(result.payload, status_code=result.status_code)

    async def _records_payload(self, run_id: str) -> dict[str, Any]:
        """The run's records, as the export carries them."""
        if not self.config.store_path:
            return {"error": "no store path configured"}
        try:
            with self._readable_store() as store:
                records = [
                    {
                        "record_id": record.record_id,
                        "coordinate": {
                            "substrate": record.substrate,
                            "geometry": record.geometry,
                            "dynamics": record.dynamics,
                            "plasticity": record.plasticity,
                            "credit": record.credit,
                            "update": record.update,
                        },
                        "schedule": record.schedule.to_dict(),
                        "payload": record.payload,
                    }
                    for record in store.query_records(run_id=run_id)
                ]
        except Exception as e:
            logger.exception("Error reading the run's records")
            return {"error": str(e)}
        return {"run_id": run_id, "records": records}

    async def _report_payload(self, run_id: str) -> dict[str, Any]:
        """The run's report, as the terminal shows it."""
        if not self.config.store_path:
            return {"error": "no store path configured"}
        try:
            from computronium.experiment.surface.report import generate_run_report

            with self._readable_store() as store:
                report = await asyncio.to_thread(generate_run_report, store, run_id)
        except Exception as e:
            logger.exception("Error reading the run's report")
            return {"error": str(e)}
        return {"run_id": run_id, "report": report}

    async def _control_payload(self) -> dict[str, Any]:
        """The plane, the run's counters, and the machine's own use.

        The HUD's CPU meter shows the queue's bookkeeping — how many CPUs the
        queue has handed out. This is the machine: how much of it is busy,
        measured rather than allocated.
        """
        state, status = self._control.read_all()
        payload: dict[str, Any] = {
            "control": state.to_dict(),
            "status": status.to_dict() if status is not None else None,
            "readable": self._control.last_error is None,
            "error": self._control.last_error,
            "machine": {
                "cpu_percent": self._cpu.read(),
                "cpu_count": os.cpu_count(),
            },
        }
        if self.config.campaign_queue is not None:
            payload["queue"] = await self.config.campaign_queue.get_resource_usage()
        return payload

    async def _apply_control(self, body: ControlCommand) -> ActionResult:
        """Merge a command into the plane, and answer with the new state."""
        state, _status = self._control.read_all()
        if body.revision is not None and body.revision != state.revision:
            return ActionResult(
                {
                    "error": "the control plane has moved on",
                    "control": state.to_dict(),
                },
                status_code=409,
            )
        given = body.model_fields_set
        changes: dict[str, Any] = {}
        if "paused" in given:
            changes["paused"] = bool(body.paused)
        if "step" in given:
            changes["step"] = bool(body.step)
        if "max_workers" in given:
            changes["max_workers"] = body.max_workers
        if "cancel" in given:
            changes["cancel"] = bool(body.cancel)
        if not changes:
            return ActionResult({"control": state.to_dict()})
        try:
            merged = self._control.write(**changes)
        except (OSError, ValueError) as exc:
            logger.exception("Could not write the control plane")
            return ActionResult(
                {"error": str(exc), "control": state.to_dict()},
                status_code=409,
            )
        return ActionResult({"control": merged.to_dict()})

    async def _start_run(self, body: RunRequest) -> ActionResult:
        """Start the run the reader asked for."""
        from computronium.experiment.execution.dashboard.runs import (
            build_spec,
            enqueue_run,
        )

        try:
            spec = build_spec(body.profile, body.overrides, device=body.device)
        except (TypeError, ValueError) as exc:
            return ActionResult({"error": str(exc)}, status_code=409)
        store_path = self.config.store_path or DEFAULT_STORE
        answer = await enqueue_run(
            self.config.campaign_queue,
            spec,
            body.overrides,
            store_path=store_path,
        )
        answer["spec"] = spec.model_dump(mode="json")
        return ActionResult(
            answer,
            status_code=200 if answer.get("started") else 409,
        )

    async def _get_status(self) -> dict[str, Any]:
        """Get overall dashboard status."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "running": self._running,
        }
        if self.config.campaign_queue:
            queue_status = await self.config.campaign_queue.get_resource_usage()
            status.update(queue_status)
        return status

    async def _get_queue_status(self) -> dict[str, Any]:
        """Get campaign queue status."""
        if not self.config.campaign_queue:
            return {"error": "No campaign queue configured"}

        queue = self.config.campaign_queue
        return {
            "max_concurrent": queue.max_concurrent,
            "queued": len(queue._queue),
            "running": len(queue._running),
            "completed": len(queue._completed),
            "resource_usage": await queue.get_resource_usage(),
        }

    async def _get_resource_usage(self) -> dict[str, Any]:
        """Get current resource usage."""
        if not self.config.campaign_queue:
            return {"error": "No campaign queue configured"}

        return await self.config.campaign_queue.get_resource_usage()

    async def _get_all_campaigns(self) -> dict[str, Any]:
        """Get all campaigns with their status."""
        if not self.config.campaign_queue:
            return {"error": "No campaign queue configured"}

        campaigns = await self.config.campaign_queue.list_campaigns()
        return {
            "campaigns": [
                {
                    "campaign_id": c.campaign_id,
                    "name": c.spec.name,
                    "status": c.status.value,
                    "priority": c.priority.name,
                    "project": c.project,
                    "user": c.user,
                    "created_at": c.created_at,
                    "scheduled_at": c.scheduled_at,
                    "started_at": c.started_at,
                    "completed_at": c.completed_at,
                    "quota": {
                        "gpus": c.quota.gpus,
                        "cpus": c.quota.cpus,
                        "memory_gb": c.quota.memory_gb,
                        "max_wall_hours": c.quota.max_wall_hours,
                    },
                    "error": c.error,
                }
                for c in campaigns
            ]
        }

    async def _get_store_runs(self) -> dict[str, Any]:
        """List the runs in the store with their record counts."""
        if not self.config.store_path:
            return {"error": "No store path configured"}

        try:
            with self._readable_store() as store:
                runs = [
                    {
                        "run_id": run.run_id,
                        "status": run.status,
                        "records": len(list(store.query_records(run_id=run.run_id))),
                    }
                    for run in store.query_runs()
                ]
        except Exception as e:
            logger.debug("Store unavailable for run listing: %s", e)
            return {"error": str(e), "runs": []}
        else:
            return {"runs": runs}

    async def _get_campaign_detail(self, campaign_id: str) -> dict[str, Any]:
        """Get detailed status for a specific campaign."""
        if not self.config.campaign_queue:
            return {"error": "No campaign queue configured"}

        entry = await self.config.campaign_queue.get_status(campaign_id)
        if not entry:
            return {"error": f"Campaign {campaign_id} not found"}

        return {
            "campaign_id": entry.campaign_id,
            "name": entry.spec.name,
            "description": "",
            "status": entry.status.value,
            "priority": entry.priority.name,
            "project": entry.project,
            "user": entry.user,
            "created_at": entry.created_at,
            "scheduled_at": entry.scheduled_at,
            "started_at": entry.started_at,
            "completed_at": entry.completed_at,
            "quota": asdict(entry.quota),
            "result": entry.result,
            "error": entry.error,
            "spec": {
                "name": entry.spec.name,
                "store": entry.spec.store,
                "parallel": entry.spec.parallel,
                "webhook_url": entry.spec.webhook_url,
                "max_wall_seconds": entry.spec.max_wall_seconds,
                "runs": [
                    {
                        "name": r.name,
                        "profile": r.profile,
                        "spec_file": r.spec_file,
                        "overrides": r.overrides,
                        "depends_on": r.depends_on,
                        "device": r.device,
                        "store": r.store,
                    }
                    for r in entry.spec.runs
                ],
            },
        }

    async def _get_campaign_metrics(self, campaign_id: str) -> dict[str, Any]:
        """Get metrics for a campaign from the store."""
        if not self.config.store_path:
            return {"error": "No store path configured"}

        try:
            with self._readable_store() as store:
                records = store.query_records()
                campaign_records = [
                    r
                    for r in records
                    if r.provenance.links.get("run_id") == campaign_id
                ]

                if not campaign_records:
                    return {
                        "metrics": [],
                        "message": "No records found for this campaign",
                    }

                metrics = []
                for r in campaign_records:
                    metrics.append({
                        "record_id": r.record_id,
                        "coordinate": {
                            "substrate": r.substrate,
                            "geometry": r.geometry,
                            "dynamics": r.dynamics,
                            "plasticity": r.plasticity,
                            "credit": r.credit,
                            "update": r.update,
                        },
                        "payload": r.payload,
                        "walltime": r.provenance.links.get("walltime_ms"),
                    })

                return {"metrics": metrics}
        except Exception as e:
            logger.exception("Error fetching campaign metrics")
            return {"error": str(e)}

    async def _get_campaign_cost(self, campaign_id: str) -> dict[str, Any]:
        """Get cost tracking data for a campaign."""
        if not self.config.store_path:
            return {"error": "No store path configured"}

        try:
            # This would need integration with the cost tracker
            return {"message": "Cost tracking data available after campaign completion"}
        except Exception as e:
            return {"error": str(e)}

    async def _get_campaign_metrics_detailed(self, campaign_id: str) -> dict[str, Any]:
        """Get detailed metrics for a campaign including Pareto and ablation data.

        This is the main endpoint for the three.js frontend. Returns:
        - records: All records serialized via RecordSerializer
        - pareto: Boolean flags indicating which records are on the Pareto frontier
        - ablation_groups: Structured ablation data from ReportGenerator

        Blocking store work runs in a thread to avoid stalling the event loop.
        """
        if not self.config.store_path:
            return {"error": "No store path configured"}

        try:
            return await asyncio.to_thread(
                self._get_campaign_metrics_detailed_sync, campaign_id
            )
        except Exception as e:
            logger.exception("Error fetching detailed campaign metrics")
            return {"error": str(e)}

    def _get_campaign_metrics_detailed_sync(self, campaign_id: str) -> dict[str, Any]:
        """Synchronous implementation of detailed campaign metrics (runs in thread)."""
        from computronium.experiment.analysis import (
            compute_pareto_frontier as analysis_compute_pareto_frontier,
        )
        from computronium.experiment.execution.statistical_promotion import (
            GateThresholds,
        )
        from computronium.experiment.surface.report import (
            ReportGenerator,
            chance_level,
            measured_cells,
        )

        # CRITICAL: read_only=True for all dashboard store access
        with self._store_view() as view:
            store = view.store
            generator = ReportGenerator(store)
            records = list(generator._store.query_records(run_id=campaign_id))
            run = store.query_run(campaign_id)
            claim_metrics = generator.claim_metrics(campaign_id)

            if not records:
                # A run that has measured nothing yet is still the run the
                # dashboard is watching: its declaration is the space the
                # map draws, and the absence of evidence is what the
                # narration reports. An empty dashboard is a dashboard
                # that has forgotten the run it is watching.
                return self._empty_run_metrics(run, campaign_id, claim_metrics, view)

            # Compute Pareto frontier over registered objectives
            pareto_points, _ = analysis_compute_pareto_frontier(
                records, list(PARETO_OBJECTIVES)
            )
            # Pareto points are keyed by measurement_key, not record_id
            pareto_ids = {p["record_id"] for p in pareto_points}

            # Get structured ablation groups
            ablation_groups = generator.get_ablation_groups(campaign_id)

            # Chance line and power requirement come from the task and the
            # gate thresholds, never from a hand-written constant.
            chance = chance_level(records[0].schedule.task_id, "validation_accuracy")

            # What the campaign has actually burned, measured.
            memory_values = [
                float(r.payload["memory_mb"])
                for r in records
                if isinstance(r.payload.get("memory_mb"), int | float)
            ]
            walltime_values = [
                float(r.payload["walltime_s"])
                for r in records
                if isinstance(r.payload.get("walltime_s"), int | float)
            ]
            seeds_per_cell: dict[tuple[str, str, str], int] = {}
            for r in records:
                key = (r.credit, r.geometry, r.dynamics)
                seeds_per_cell[key] = seeds_per_cell.get(key, 0) + 1
            resources = {
                "device": records[0].schedule.device,
                "memory_mb": max(memory_values, default=0.0),
                "walltime_s": sum(walltime_values),
                "records": len(records),
                "seeds_per_arm": max(seeds_per_cell.values(), default=0),
            }

            return {
                "records": [serializer.to_api_dict(r) for r in records],
                "pareto": [r.measurement_key in pareto_ids for r in records],
                "ablation_groups": ablation_groups,
                "chance": chance,
                "required_seeds": GateThresholds().required_seeds_per_group,
                "gate": GateThresholds().to_dict(),
                "resources": resources,
                "store": {
                    "source": view.source,
                    "published_at": (
                        view.published_at.isoformat() if view.published_at else None
                    ),
                },
                "run": run_status(
                    run.spec if run else None,
                    campaign_id,
                    claim_metrics,
                    run.started_at if run else None,
                    measured_cells(records),
                    run.status if run else None,
                ),
            }

    def _empty_run_metrics(
        self,
        run: Any,
        run_id: str,
        claim_metrics: tuple[str, ...],
        view: Any,
    ) -> dict[str, Any]:
        """What the dashboard knows about a run that has measured nothing yet.

        The run's declaration is enough to draw its space and to say what it
        is: the profile, the task, the mode, the cells it declared. The
        numbers are zero because nothing has been measured — and zero is the
        honest answer, not a gap to be filled with a guess.
        """
        from computronium.experiment.execution.statistical_promotion import (
            GateThresholds,
        )
        from computronium.experiment.surface.report import chance_level

        spec = run.spec if run else None
        task = spec.task_names[0] if spec and spec.task_names else None
        return {
            "records": [],
            "pareto": [],
            "ablation_groups": [],
            "chance": chance_level(task, "validation_accuracy"),
            "required_seeds": GateThresholds().required_seeds_per_group,
            "gate": GateThresholds().to_dict(),
            "resources": {
                "device": "—",
                "memory_mb": 0.0,
                "walltime_s": 0.0,
                "records": 0,
                "seeds_per_arm": 0,
            },
            "store": {
                "source": view.source,
                "published_at": (
                    view.published_at.isoformat() if view.published_at else None
                ),
            },
            "run": run_status(
                spec,
                run_id,
                claim_metrics,
                run.started_at if run else None,
                frozenset(),
                run.status if run else None,
            ),
        }

    def _cell_context(self, run_id: str, body: CellAction) -> CellContext:
        """Everything an action needs to know about one cell.

        Raises:
            ActionUnavailableError: The store is not attached, or the run is not
                in it.
        """
        from computronium.experiment.execution.statistical_promotion import (
            GateThresholds,
        )
        from computronium.experiment.surface.report import (
            ReportGenerator,
            chance_level,
        )

        if not self.config.store_path:
            raise ActionUnavailableError("no store path configured")

        with self._readable_store() as store:
            info = store.query_run(run_id)
            if info is None or info.spec is None:
                raise ActionUnavailableError(f"run {run_id} is not in the store")
            source = info.spec
            run_records = list(store.query_records(run_id=run_id))
            metrics = ReportGenerator(store).claim_metrics(run_id)

        metric = metrics[0] if metrics else default_metric()
        target = CellTarget(run_id=run_id, coordinate=body.coordinate)
        records = records_for_cell(run_records, target.coordinate)
        # A cell nobody measured has no record to name its task, but the run
        # does: the chance level a claim is measured against is the run's.
        task_id = (
            records[0].schedule.task_id
            if records
            else (source.task_names[0] if source.task_names else "")
        )
        gate = GateThresholds()

        return CellContext(
            source=source,
            target=target,
            records=records,
            run_records=run_records,
            metric=metric,
            task_id=task_id,
            chance=chance_level(task_id or None, metric),
            required_seeds=gate.required_seeds_per_group,
            alpha=gate.alpha,
        )

    async def _cell_space(self, run_id: str, body: SpaceRequest) -> ActionResult:
        """The declared space the grid shows, and the system's verdict on it.

        The space is the ontology's, cut to a slice: three axes free, the rest
        held at one value each, so every cell on the grid is a whole
        coordinate the system can judge.
        """
        from computronium.experiment.execution.dashboard.space import declared_space

        try:
            axes = resolve_axes(body.axes)
        except ValueError as exc:
            return ActionResult({"error": str(exc)}, status_code=409)

        if not self.config.store_path:
            return ActionResult({"error": "no store path configured"}, status_code=409)

        with self._readable_store() as store:
            info = store.query_run(run_id)
            if info is None or info.spec is None:
                return ActionResult(
                    {"error": f"run {run_id} is not in the store"},
                    status_code=409,
                )
            spec = info.spec
            records = list(store.query_records(run_id=run_id))

        task = spec.task_names[0] if spec.task_names else None
        if not task and records:
            task = records[0].schedule.task_id or None

        payload = declared_space(spec, records, axes, task=task)
        payload["run_id"] = run_id
        return ActionResult(payload)

    async def _replicate_cell(self, run_id: str, body: CellAction) -> ActionResult:
        """Queue the measurements a cell still owes."""
        from computronium.experiment.execution.campaign import (
            CampaignRun,
            CampaignSpec,
        )

        queue = self.config.campaign_queue
        if queue is None:
            return ActionResult(
                {"error": "no campaign queue is attached to this dashboard"},
                status_code=409,
            )

        try:
            context = self._cell_context(run_id, body)
        except ActionUnavailableError as exc:
            return ActionResult({"error": str(exc)}, status_code=409)

        refusal = self._refusal(context)
        if refusal:
            return ActionResult({"error": refusal}, status_code=409)

        measured = len(context.records)
        missing = max(0, context.required_seeds - measured)
        seeds = body.seeds or missing
        if seeds <= 0:
            return ActionResult(
                {"error": "the cell already holds the seeds a claim asks for"},
                status_code=409,
            )

        # The plan is the seeds the cell has plus the ones it still owes: the
        # run's own plan covers the seeds it already measured, and a cell it
        # never measured owes the gate's count and no more.
        plan = measured + seeds
        measurements = plan - measured
        per_seed = self._per_seed_seconds(context)
        budget = measurement_budget(per_seed, measurements)

        spec = cell_spec(
            context.source,
            context.target,
            seeds=plan,
            budget_seconds=budget,
        )
        spec_path = self._write_spec(spec)

        campaign = CampaignSpec(
            name=f"replicate-{context.target.slug()}",
            runs=[
                CampaignRun(
                    name=f"replicate-{run_id}",
                    spec_file=str(spec_path),
                    store=self.config.store_path or "experiment.duckdb",
                    run_id=run_id,
                )
            ],
            store=self.config.store_path or "experiment.duckdb",
        )
        campaign_id = await queue.enqueue(campaign)

        return ActionResult({
            "campaign_id": campaign_id,
            "run_id": run_id,
            "measurements": measurements,
            "plan": plan,
            "budget_seconds": budget,
            "spec_file": str(spec_path),
        })

    async def _preregister_cell(self, run_id: str, body: CellAction) -> ActionResult:
        """Register the protocol a confirming run of this cell must meet."""
        try:
            context = self._cell_context(run_id, body)
        except ActionUnavailableError as exc:
            return ActionResult({"error": str(exc)}, status_code=409)

        if not context.records:
            return ActionResult(
                {
                    "error": (
                        "the cell carries no measurement to confirm; "
                        "adopt it as a quest instead"
                    )
                },
                status_code=409,
            )

        chance = context.chance or 0.0
        threshold = body.threshold
        if threshold is None:
            threshold = round(self._measured_effect(context) - chance, 6)

        payload = registration_payload(
            context.target,
            claim=claim_sentence(
                context.target,
                metric=context.metric,
                task=context.task_id or "the task",
                chance=chance,
                threshold=threshold,
                min_seeds=body.min_seeds or context.required_seeds,
                kind=KIND_CONFIRMATION,
            ),
            metric=context.metric,
            threshold=threshold,
            alpha=body.alpha or context.alpha,
            min_seeds=body.min_seeds or context.required_seeds,
            kind=KIND_CONFIRMATION,
        )
        return self._write_registration(context, payload, KIND_CONFIRMATION)

    async def _adopt_quest(self, run_id: str, body: CellAction) -> ActionResult:
        """Register the question an unmeasured cell answers, and queue the run
        that would answer it.

        A question with no run behind it is a note. The quest writes the
        protocol down first and queues the measurement second: the run that
        follows the registration can be confirmatory, and a run that began
        before it cannot.
        """
        from computronium.experiment.execution.statistical_promotion import (
            GateThresholds,
        )

        try:
            context = self._cell_context(run_id, body)
        except ActionUnavailableError as exc:
            return ActionResult({"error": str(exc)}, status_code=409)

        if context.records:
            return ActionResult(
                {
                    "error": (
                        "the cell is already measured; "
                        "preregister the confirmation instead"
                    )
                },
                status_code=409,
            )

        refusal = self._refusal(context)
        if refusal:
            return ActionResult({"error": refusal}, status_code=409)

        threshold = body.threshold
        if threshold is None:
            spread = run_spread(context.run_records, context.metric)
            if spread <= 0.0:
                return ActionResult(
                    {
                        "error": (
                            "the run has no measured spread to state the effect "
                            "in; declare the threshold yourself"
                        )
                    },
                    status_code=409,
                )
            threshold = round(GateThresholds().effect_size_target * spread, 6)

        chance = context.chance or 0.0
        payload = registration_payload(
            context.target,
            claim=claim_sentence(
                context.target,
                metric=context.metric,
                task=context.task_id or "the task",
                chance=chance,
                threshold=threshold,
                min_seeds=body.min_seeds or context.required_seeds,
                kind=KIND_QUEST,
            ),
            metric=context.metric,
            threshold=threshold,
            alpha=body.alpha or context.alpha,
            min_seeds=body.min_seeds or context.required_seeds,
            kind=KIND_QUEST,
        )
        written = self._write_registration(context, payload, KIND_QUEST)
        if written.status_code != 200:
            return written
        scheduled = await self._schedule_quest(context, body)
        return ActionResult({**written.payload, **scheduled})

    async def _schedule_quest(
        self,
        context: CellContext,
        body: CellAction,
    ) -> dict[str, Any]:
        """Queue the run that would answer a registered question.

        The run is a new one. A threshold written now cannot confirm a run
        that has already begun, so the run that answers the question has to
        begin after the question was written — and the source run began long
        before. The cell holds no evidence to join either: every seed in the
        plan is new.
        """
        from computronium.experiment.execution.campaign import (
            CampaignRun,
            CampaignSpec,
        )

        queue = self.config.campaign_queue
        if queue is None:
            return {
                "campaign_id": None,
                "scheduled": False,
                "note": (
                    "no campaign queue is attached to this dashboard; the "
                    "question is registered but nothing is scheduled"
                ),
            }

        seeds = body.min_seeds or context.required_seeds
        per_seed = self._per_seed_seconds(context)
        budget = measurement_budget(per_seed, seeds)
        spec = cell_spec(
            context.source,
            context.target,
            seeds=seeds,
            budget_seconds=budget,
        )
        spec_path = self._write_spec(spec)

        store = self.config.store_path or "experiment.duckdb"
        campaign = CampaignSpec(
            name=f"quest-{context.target.slug()}",
            runs=[
                CampaignRun(
                    name=f"quest-{context.target.run_id}",
                    spec_file=str(spec_path),
                    store=store,
                )
            ],
            store=store,
        )
        campaign_id = await queue.enqueue(campaign)
        return {
            "campaign_id": campaign_id,
            "scheduled": True,
            "measurements": seeds,
            "plan": seeds,
            "budget_seconds": budget,
            "spec_file": str(spec_path),
        }

    def _write_registration(
        self,
        context: CellContext,
        payload: dict[str, Any],
        kind: str,
    ) -> ActionResult:
        """Write a registration into the registry the report reads."""
        directory = self._registration_directory()
        name = registration_name(context.target, kind)
        try:
            path, written = write_registration(directory, payload, name=name)
        except FileExistsError as exc:
            return ActionResult({"error": str(exc)}, status_code=409)
        return ActionResult({
            "path": str(path),
            "written": written,
            "registration": payload,
        })

    def _registration_directory(self) -> Path:
        """Where the dashboard writes the registrations it produces."""
        if self.config.registration_dir is not None:
            return self.config.registration_dir
        from computronium.experiment.surface.report import PREREGISTRATION_ROOT

        return PREREGISTRATION_ROOT

    def _refusal(self, context: CellContext) -> str | None:
        """Why the system refuses this cell, or ``None`` when it does not.

        A cell the system's own void rules reject cannot be measured, so
        neither a replication nor a registration may name it. The grid marks
        those cells void, and the verbs agree with the mark.
        """
        from computronium.experiment.execution.dashboard.space import void_reason

        task = context.source.task_names[0] or context.task_id or None
        reason = void_reason(context.target.coordinate, task)
        if reason is None:
            return None
        return f"the system refuses this cell — {reason}"

    def _measured_effect(self, context: CellContext) -> float:
        """The effect the cell showed, in the metric's own units."""
        values = [
            float(record.payload[context.metric])
            for record in context.records
            if isinstance(record.payload.get(context.metric), int | float)
        ]
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _per_seed_seconds(self, context: CellContext) -> float:
        """What one measurement costs, measured where it can be measured."""
        own = cell_evidence(context.records, context.metric).walltime_s
        if own > 0.0:
            return own
        return cell_evidence(context.run_records, context.metric).walltime_s

    def _write_spec(self, spec: RunSpec) -> Path:
        """Write the declaration a queued campaign runs from."""
        directory = self._scratch_dir()
        path = directory / f"{spec.profile}-{uuid.uuid4().hex[:8]}.json"
        path.write_text(json.dumps(spec.to_dict(), indent=2), encoding="utf-8")
        return path

    def _scratch_dir(self) -> Path:
        """The dashboard's scratch directory for the declarations it launches."""
        if self._work_dir is None:
            self._work_dir = Path(tempfile.mkdtemp(prefix="computronium-dashboard-"))
        return self._work_dir

    @contextlib.contextmanager
    def _store_view(self) -> Generator[StoreView]:
        """The store to read: the live one, or the mirror a writer published.

        DuckDB allows one writer at a time, and its lock on the file is
        exclusive: a read-only connection cannot join a read-write one — not
        even in the same process, where DuckDB shares one instance per path —
        and a reader in another process cannot open a file a writer holds at
        all. So the dashboard reads the store when it can, and reads the
        writer's published mirror when the writer is elsewhere.
        """
        from computronium.experiment.evidence.mirror import readable_store

        path = Path(self.config.store_path or "")
        with readable_store(path) as view:
            yield view

    @contextlib.contextmanager
    def _readable_store(self) -> Generator[RecordStore]:
        """Open the store for reading, tolerating a live writer."""
        with self._store_view() as view:
            yield view.store

    async def _handle_websocket(self, websocket: WebSocket) -> None:
        """Handle WebSocket connections for real-time updates."""
        await websocket.accept()
        self._connected_websockets.add(websocket)
        self._ws_locks[websocket] = asyncio.Lock()
        logger.info(f"WebSocket connected. Total: {len(self._connected_websockets)}")

        # A client that arrives late still sees what happened.
        await self._replay_events(websocket)

        try:
            # Keep the connection alive; handle incoming messages (ping/pong).
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if message.get("type") == "ping":
                    await self._send_json(websocket, {"type": "pong"})
        except WebSocketDisconnect:
            pass
        except Exception:
            logger.exception("WebSocket error")
        finally:
            self._connected_websockets.discard(websocket)
            self._ws_locks.pop(websocket, None)
            logger.info(
                f"WebSocket disconnected. Total: {len(self._connected_websockets)}"
            )

    async def _send_json(self, websocket: WebSocket, message: dict[str, Any]) -> bool:
        """Send JSON to a single websocket with its lock. Returns True on success."""
        lock = self._ws_locks.get(websocket)
        if lock is None:
            return False
        async with lock:
            try:
                await websocket.send_json(message)
                return True
            except Exception:
                return False

    async def _replay_events(self, websocket: WebSocket) -> None:
        """Send the recent events to a client that just connected."""
        # Ensure the socket has a lock for _send_json
        if websocket not in self._ws_locks:
            self._ws_locks[websocket] = asyncio.Lock()

        for message in list(self._event_history)[-50:]:
            await self._send_json(websocket, message)

        # Also send the latest campaign metrics for any run with records,
        # so a late-joining client gets the current picture immediately.
        if not self.config.store_path:
            return

        try:
            logger.info("Sending initial campaign metrics on connect")
            with self._readable_store() as store:
                runs = store.query_runs()
                logger.info(f"Found {len(list(runs))} runs in store")
                for run in runs:
                    count = store.count_records(run_id=run.run_id)
                    logger.info(
                        f"Run {run.run_id}: status={run.status}, records={count}"
                    )
                    if run.status == "running" or count:
                        metrics = await self._get_campaign_metrics_detailed(run.run_id)
                        if metrics.get("run"):
                            logger.info(f"Sending campaign_metrics for {run.run_id}")
                            await self._send_json(
                                websocket,
                                {
                                    "type": "campaign_metrics",
                                    "campaign_id": run.run_id,
                                    "data": metrics,
                                    "timestamp": datetime.now().isoformat(),
                                },
                            )
        except Exception:
            logger.exception("Could not send initial campaign metrics on connect")

    async def _broadcast_update(self, message: dict[str, Any]) -> None:
        """Broadcast message to all connected WebSocket clients."""
        if not self._connected_websockets:
            return

        # Iterate over a tuple to avoid mutation during iteration.
        for ws in tuple(self._connected_websockets):
            lock = self._ws_locks.get(ws)
            if lock is None:
                # Backward compat: create lock for sockets added directly to set
                lock = asyncio.Lock()
                self._ws_locks[ws] = lock
            async with lock:
                try:
                    await ws.send_json(message)
                except Exception:
                    self._connected_websockets.discard(ws)
                    self._ws_locks.pop(ws, None)

    async def start(self) -> None:
        """Start the dashboard update loop."""
        self._running = True
        self._loop = asyncio.get_running_loop()
        self._unsubscribe = get_event_bus().subscribe(self._on_pipeline_event)
        if self.config.enable_websockets:
            self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Dashboard started")

    async def stop(self) -> None:
        """Stop the dashboard update loop."""
        self._running = False
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        if self._update_task:
            self._update_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._update_task
        if self._work_dir is not None:
            shutil.rmtree(self._work_dir, ignore_errors=True)
            self._work_dir = None
        logger.info("Dashboard stopped")

    def _on_pipeline_event(self, event: PipelineEvent) -> None:
        """Forward a live event to the clients.

        The bus is process-local and the run may publish from any thread, so
        the broadcast is scheduled onto the dashboard's loop rather than
        awaited here. The frame carries the event's *sentence*: the wording is
        written once, on the server, so the caption, the rail and an agent
        reading the story all say the same thing.
        """
        loop = self._loop
        if loop is None or loop.is_closed():
            return
        if event.run_id:
            self._reported_runs.add(event.run_id)
        line = self._narration.event(event)
        message = event.to_message()
        message["sentence"] = line.text
        self._event_history.append(message)
        loop.call_soon_threadsafe(
            lambda: loop.create_task(self._broadcast_update(message))
        )

    async def _update_loop(self) -> None:
        """Background loop to broadcast updates."""
        while self._running:
            try:
                await asyncio.sleep(self.config.update_interval)
                if not self._running:
                    break

                status = await self._get_status()
                queue_status = await self._get_queue_status()

                # Send individual updates that frontend handlers expect
                await self._broadcast_update({
                    "type": "status_update",
                    "data": status,
                    "timestamp": datetime.now().isoformat(),
                })
                await self._broadcast_update({
                    "type": "queue_update",
                    "data": queue_status,
                    "timestamp": datetime.now().isoformat(),
                })

                # Also send combined periodic update for any listeners that want it
                await self._broadcast_update({
                    "type": "periodic_update",
                    "status": status,
                    "queue": queue_status,
                    "timestamp": datetime.now().isoformat(),
                })

                await self._broadcast_campaign_metrics()
                await self._broadcast_store_metrics()
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in dashboard update loop")
                await asyncio.sleep(5)

    async def _broadcast_campaign_metrics(self) -> None:
        """Metrics for the campaigns the queue is running."""
        if not self.config.campaign_queue:
            return

        campaigns = await self._get_all_campaigns()
        for campaign in campaigns.get("campaigns", []):
            campaign_id = campaign["campaign_id"]
            status = campaign["status"]
            # Only send detailed metrics for running campaigns
            if status != "running":
                continue
            # Get record count for cache key
            record_count = 0
            if self.config.store_path:
                try:
                    with self._readable_store() as store:
                        record_count = store.count_records(run_id=campaign_id)
                except Exception:
                    pass
            await self._maybe_send_metrics(campaign_id, status, record_count)

    async def _broadcast_store_metrics(self) -> None:
        """Metrics for every run with records in the store.

        This covers campaigns run directly via the CLI, which never touch the
        queue.
        """
        if not self.config.store_path:
            return

        try:
            # Fetch run IDs with records in a thread to avoid blocking.
            run_ids, newest_id = await asyncio.to_thread(self._get_store_run_ids_sync)

            # Get record counts for all runs in one query
            record_counts = await asyncio.to_thread(
                self._get_record_counts_sync, run_ids
            )

            # A run writing from another process shows up here as records
            # landing in the store — the only progress a cross-process
            # dashboard can honestly report.
            self._announce_store_progress(record_counts)

            for run_id in run_ids:
                record_count = record_counts.get(run_id, 0)
                # Get run status
                run_status = "unknown"
                try:
                    with self._readable_store() as store:
                        run = store.query_run(run_id)
                        if run:
                            run_status = run.status
                except Exception:
                    pass
                await self._maybe_send_metrics(run_id, run_status, record_count)
                if newest_id is not None and run_id == newest_id:
                    # Still need to send metrics to get narration
                    metrics = await self._get_cached_metrics(
                        run_id, run_status, record_count
                    )
                    await self._refresh_narration(metrics)
        except Exception:
            logger.debug("Store unavailable for broadcast", exc_info=True)

    async def _maybe_send_metrics(
        self, run_id: str, status: str, record_count: int
    ) -> None:
        """Send metrics only if cache key changed (running) or never sent (finished)."""
        cache_key = (run_id, record_count, status)
        cached = self._metrics_cache.get(cache_key)

        if cached is not None:
            # Cache hit: metrics haven't changed, send cached version
            await self._broadcast_update({
                "type": "campaign_metrics",
                "campaign_id": run_id,
                "data": cached,
                "timestamp": datetime.now().isoformat(),
            })
            return

        # Cache miss: compute and cache
        metrics = await self._get_campaign_metrics_detailed(run_id)
        if not metrics.get("run"):
            # Run not ready yet, don't cache or send
            return

        # Cache the metrics
        self._metrics_cache[cache_key] = metrics

        # For finished runs, we can also store with a special "finished" key
        # so we don't recompute if status changes to finished
        if status != "running":
            finished_key = (run_id, record_count, "finished")
            self._metrics_cache[finished_key] = metrics

        await self._broadcast_update({
            "type": "campaign_metrics",
            "campaign_id": run_id,
            "data": metrics,
            "timestamp": datetime.now().isoformat(),
        })

    async def _get_cached_metrics(
        self, run_id: str, status: str, record_count: int
    ) -> dict[str, Any]:
        """Get metrics from cache or compute if missing."""
        cache_key = (run_id, record_count, status)
        if cache_key in self._metrics_cache:
            return self._metrics_cache[cache_key]
        # Compute and cache
        metrics = await self._get_campaign_metrics_detailed(run_id)
        if metrics.get("run"):
            self._metrics_cache[cache_key] = metrics
            if status != "running":
                finished_key = (run_id, record_count, "finished")
                self._metrics_cache[finished_key] = metrics
        return metrics

    def _get_store_run_ids_sync(self) -> tuple[list[str], str | None]:
        """Synchronous helper to get run IDs with records and the newest run ID."""
        with self._readable_store() as store:
            runs = store.query_runs()
            record_counts = store.count_records_by_run()
            run_ids = [
                run.run_id
                for run in runs
                if run.status == "running" or record_counts.get(run.run_id, 0)
            ]

            # The run the dashboard is about is the one that started last, and
            # the browser picks the same one: the picture and the narration
            # must be about the same run.
            newest = max(
                (run for run in runs if run.run_id in run_ids),
                key=lambda run: run.started_at,
                default=None,
            )
            return run_ids, newest.run_id if newest else None

    def _get_record_counts_sync(self, run_ids: list[str]) -> dict[str, int]:
        """Synchronous helper to get record counts for runs."""
        with self._readable_store() as store:
            all_counts = store.count_records_by_run()
            return {run_id: all_counts.get(run_id, 0) for run_id in run_ids}

    async def _refresh_narration(self, metrics: dict[str, Any]) -> None:
        """Say what the system is doing, now, and tell the clients.

        The sentences are the dashboard's own account of itself: the run, how
        much of it exists, what the best cell scored, what a claim still
        needs, and what the machine is doing. A reader who sees only the
        screen can say all of it.
        """
        run = metrics.get("run") or {}
        queue = await self._get_queue_status()
        state, _status = self._control.read_all()
        sentences = state_sentences(metrics, queue, control=state.to_dict())
        self._narration.state(sentences, run_id=run.get("run_id"))
        await self._broadcast_update({
            "type": "narration",
            "state": list(sentences),
            "timestamp": datetime.now().isoformat(),
        })

    async def _narration_payload(self, run_id: str | None = None) -> dict[str, Any]:
        """The dashboard's account of itself, for a reader without a browser."""
        payload: dict[str, Any] = {
            "state": list(self._narration.current()),
            "lines": [asdict(line) for line in self._narration.lines()],
            "script": self._narration.script(),
        }
        if run_id and run_id != self._narration.current_run_id:
            # A reader may ask about a run the dashboard is not showing.
            metrics = await self._get_campaign_metrics_detailed(run_id)
            if metrics.get("records"):
                queue = await self._get_queue_status()
                state, _status = self._control.read_all()
                payload["state"] = list(
                    state_sentences(metrics, queue, control=state.to_dict())
                )
        return payload

    def _event_payload(self, run_id: str | None = None) -> dict[str, Any]:
        """The run's events, and the stages they came from.

        The events are the ones this dashboard saw: the bus is process-local,
        so a run that happened in another process has no timeline here, and
        the picture says so rather than inventing one.
        """
        from computronium.experiment.execution.events import stage_spans

        frames = [
            frame
            for frame in self._event_history
            if run_id is None or frame.get("run_id") == run_id
        ]
        spans = stage_spans(frames)
        first = min((span.first for span in spans), default=0.0)
        last = max((span.last for span in spans), default=0.0)
        return {
            "run_id": run_id,
            "start": first,
            "seconds": last - first,
            "events": [
                {
                    "stage": frame.get("stage"),
                    "message": frame.get("message"),
                    "level": frame.get("level"),
                    "sentence": frame.get("sentence"),
                    "at": frame.get("at"),
                }
                for frame in frames
            ],
            "stages": [asdict(span) for span in spans],
        }

    async def _account_payload(self, run_id: str) -> dict[str, Any]:
        """The run's account: what it can say, and how its arms compare."""
        from computronium.experiment.execution.dashboard.ledger import (
            contrast_payload,
            ledger_payload,
        )

        if not self.config.store_path:
            return {"error": "no store path configured"}
        try:
            with self._readable_store() as store:
                return {
                    "run_id": run_id,
                    "ledger": ledger_payload(store, run_id),
                    "contrast": contrast_payload(store, run_id),
                }
        except Exception as e:
            logger.exception("Error reading the run's account")
            return {"error": str(e)}

    def _flow_payload(self, run_id: str) -> dict[str, Any]:
        """The run's cells, from the space to the evidence.

        The flow is read from the events this dashboard watched, so a run
        that happened elsewhere has no flow here — and the picture says so
        rather than drawing a run it never saw.
        """
        from computronium.experiment.execution.dashboard.flow import flow_payload

        frames = [
            frame for frame in self._event_history if frame.get("run_id") == run_id
        ]
        return flow_payload(frames, run_id)

    async def _attribution_payload(self, run_id: str) -> dict[str, Any]:
        """What the run can attribute, and what its design cannot say."""
        from computronium.experiment.execution.dashboard.attribution import (
            attribution_payload,
        )

        if not self.config.store_path:
            return {"error": "no store path configured"}
        try:
            with self._readable_store() as store:
                return attribution_payload(store, run_id)
        except Exception as e:
            logger.exception("Error reading the run's attribution")
            return {"error": str(e)}

    async def _dynamics_payload(self, run_id: str) -> dict[str, Any]:
        """The run's own cell, and the dynamics it does or does not have.

        The measurement is expensive — the cell is composed, and its own
        relaxation is measured over hundreds of steps — so it is kept: the
        answer does not change while the run does.
        """
        if not self.config.store_path:
            return {"error": "no store path configured"}
        cached = self._dynamics_cache.get(run_id)
        if cached is not None:
            return cached
        try:
            payload = await asyncio.to_thread(self._measure_dynamics, run_id)
        except Exception as e:
            logger.exception("Error measuring the cell's dynamics")
            return {"error": str(e)}
        # A run that has measured nothing yet is not an answer: it is a run
        # that has not started, and the answer comes when it has.
        if payload.get("cell") is not None:
            self._dynamics_cache[run_id] = payload
        return payload

    def _measure_dynamics(self, run_id: str) -> dict[str, Any]:
        """The measurement, with the store opened where it is used.

        DuckDB's connection belongs to the thread that opened it, so the
        store is opened inside the work rather than handed to it.
        """
        from computronium.experiment.execution.dashboard.dynamics import run_dynamics

        with self._readable_store() as store:
            return run_dynamics(store, run_id)

    async def _trained_dynamics_payload(self, run_id: str) -> dict[str, Any]:
        """The run's cell, trained first, then its dynamics measured.

        The measurement is expensive — the cell is composed, trained, and its
        relaxation measured — so it is cached: the answer does not change
        while the run does.
        """
        if not self.config.store_path:
            return {"error": "no store path configured"}
        cache_key = f"{run_id}_trained"
        cached = self._dynamics_cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            payload = await asyncio.to_thread(self._measure_trained_dynamics, run_id)
        except Exception as e:
            logger.exception("Error measuring the trained cell's dynamics")
            return {"error": str(e)}
        if payload.get("cell") is not None:
            self._dynamics_cache[cache_key] = payload
        return payload

    def _measure_trained_dynamics(self, run_id: str) -> dict[str, Any]:
        """The trained measurement, with the store opened where it is used."""
        from computronium.experiment.execution.dashboard.dynamics import (
            run_trained_dynamics,
        )

        with self._readable_store() as store:
            return run_trained_dynamics(store, run_id)

    async def _spaces_payload(self, body: SpaceRequest) -> dict[str, Any]:
        """The runs' evidence in one space.

        Reading a slice of the space is expensive — the system's own void
        rules are evaluated for every cell of it — so the work is done off
        the event loop, and what was read is kept.
        """
        try:
            axes = resolve_axes(body.axes)
        except ValueError as exc:
            return {"error": str(exc)}
        if not self.config.store_path:
            return {"error": "no store path configured"}
        try:
            return await asyncio.to_thread(self._read_spaces, axes)
        except Exception as e:
            logger.exception("Error reading the runs' space")
            return {"error": str(e)}

    def _read_spaces(self, axes: list[StructuralAxis]) -> dict[str, Any]:
        """The runs' evidence, with the store opened where it is used."""
        with self._readable_store() as store:
            return multirun_payload(self._space_reader, store, axes)

    def _announce_store_progress(self, record_counts: dict[str, int]) -> None:
        """Report records that landed in the store since the last poll.

        A run that reports itself on the event bus (the pipeline running in
        this process) already says what it measured, so only runs nobody is
        reporting for are counted here.
        """
        for run_id, count in record_counts.items():
            previous = self._run_record_counts.get(run_id)
            self._run_record_counts[run_id] = count
            if previous is None or count <= previous:
                continue
            if run_id in self._reported_runs:
                continue
            publish_event(
                "s8_record",
                f"run {run_id[:8]}: {count - previous} new cells ({count} total)",
                run_id=run_id,
                detail={"records": count},
            )

    async def run(self) -> None:
        """Run the dashboard server (blocking)."""
        import uvicorn

        await self.start()
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
            # Uvicorn's own logging config disables every logger it does not
            # name, and the tour's logger is one of them: a tour that failed
            # said nothing. The dashboard keeps the logging it was given.
            log_config=None,
        )
        server = uvicorn.Server(config)
        try:
            await server.serve()
        finally:
            await self.stop()


def create_dashboard(
    config: DashboardConfig | None = None,
) -> WebDashboard:
    """Factory function to create a web dashboard."""
    return WebDashboard(config)


def create_dashboard_app(
    config: DashboardConfig | None = None,
):
    """ASGI factory function for uvicorn --factory."""
    dashboard = WebDashboard(config)
    return dashboard.app


async def run_dashboard(
    host: str = "0.0.0.0",
    port: int = 8080,
    store_path: str | None = None,
    campaign_queue: CampaignQueue | None = None,
) -> None:
    """Convenience function to run the dashboard."""
    config = DashboardConfig(
        host=host,
        port=port,
        store_path=store_path,
        campaign_queue=campaign_queue,
    )
    dashboard = create_dashboard(config)
    await dashboard.run()
