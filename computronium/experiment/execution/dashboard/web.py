"""Web Dashboard for Live Campaign Monitoring (Phase E5).

FastAPI-based web dashboard with three.js frontend for real-time updates.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from computronium.experiment.evidence.serializers import serializer

if TYPE_CHECKING:
    from collections.abc import Generator

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.campaign_queue import (
        CampaignQueue,
    )

logger = logging.getLogger(__name__)

# Pareto objectives: maximize task accuracy, minimize wall cost.
PARETO_OBJECTIVES = ("validation_accuracy", "walltime_total")


@dataclass(frozen=True, slots=True)
class DashboardConfig:
    """Configuration for the web dashboard."""

    host: str = "0.0.0.0"
    port: int = 8080
    update_interval: float = 2.0  # seconds
    store_path: str | None = None
    campaign_queue: CampaignQueue | None = None
    enable_websockets: bool = True
    template_dir: Path | None = None
    static_dir: Path | None = None
    read_only: bool = True  # Dashboard never writes: avoids DuckDB lock contention


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
        self.config = config or DashboardConfig()
        self.app = FastAPI(title="Computronium Campaign Dashboard")
        self._connected_websockets: set[WebSocket] = set()
        self._running = False
        self._update_task: asyncio.Task | None = None
        self._setup_routes()
        self._setup_templates()

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
            return {"runs": runs}
        except Exception as e:
            logger.debug("Store unavailable for run listing: %s", e)
            return {"error": str(e), "runs": []}

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
        """
        if not self.config.store_path:
            return {"error": "No store path configured"}

        try:
            from computronium.experiment.execution.statistical_promotion import (
                GateThresholds,
            )
            from computronium.experiment.surface.report import (
                ReportGenerator,
                chance_level,
            )
            from computronium.experiment.analysis import (
                compute_pareto_frontier as analysis_compute_pareto_frontier,
            )

            # CRITICAL: read_only=True for all dashboard store access
            with self._readable_store() as store:
                generator = ReportGenerator(store)
                records = list(generator._store.query_records(run_id=campaign_id))

                if not records:
                    return {
                        "records": [],
                        "pareto": [],
                        "ablation_groups": [],
                        "message": "No records found for this campaign",
                    }

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
                chance = chance_level(
                    records[0].schedule.task_id, "validation_accuracy"
                )

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
                    "resources": resources,
                }
        except Exception as e:
            logger.exception("Error fetching detailed campaign metrics")
            return {"error": str(e)}

    @contextlib.contextmanager
    def _readable_store(self) -> Generator[RecordStore, None, None]:
        """Open the store for reading, tolerating a live writer.

        DuckDB allows one writer at a time, and a read-only connection cannot
        join a read-write one — not even in the same process, where DuckDB
        shares one instance per path. So the dashboard opens read-only first
        (which coexists with a writer in another process) and falls back to
        read-write when the writer is this process, which is how an in-process
        campaign stays visible while it runs.
        """
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        path = Path(self.config.store_path or "")
        modes = (True, False) if self.config.read_only else (False,)
        failure: Exception | None = None

        for read_only in modes:
            if not read_only and not path.exists():
                # The dashboard never brings a store into being.
                break
            with contextlib.ExitStack() as stack:
                store = RecordStore(StoreConfig(path=path, read_only=read_only))
                try:
                    stack.enter_context(store)
                except Exception as exc:
                    failure = exc
                    continue
                yield store
                return

        msg = f"store {path} is held by another writer: {failure}"
        raise RuntimeError(msg)

    async def _handle_websocket(self, websocket: WebSocket) -> None:
        """Handle WebSocket connections for real-time updates."""
        await websocket.accept()
        self._connected_websockets.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self._connected_websockets)}")

        try:
            while True:
                # Send periodic updates
                await asyncio.sleep(self.config.update_interval)
                if not self._running:
                    break

                status = await self._get_status()
                await websocket.send_json({
                    "type": "status_update",
                    "data": status,
                    "timestamp": datetime.now().isoformat(),
                })

                queue_status = await self._get_queue_status()
                await websocket.send_json({
                    "type": "queue_update",
                    "data": queue_status,
                    "timestamp": datetime.now().isoformat(),
                })
        except WebSocketDisconnect:
            pass
        except Exception:
            logger.exception("WebSocket error")
        finally:
            self._connected_websockets.discard(websocket)
            logger.info(
                f"WebSocket disconnected. Total: {len(self._connected_websockets)}"
            )

    async def _broadcast_update(self, message: dict[str, Any]) -> None:
        """Broadcast message to all connected WebSocket clients."""
        if not self._connected_websockets:
            return

        dead = set()
        for ws in self._connected_websockets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)

        for ws in dead:
            self._connected_websockets.discard(ws)

    async def start(self) -> None:
        """Start the dashboard update loop."""
        self._running = True
        if self.config.enable_websockets:
            self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Dashboard started")

    async def stop(self) -> None:
        """Stop the dashboard update loop."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("Dashboard stopped")

    async def _update_loop(self) -> None:
        """Background loop to broadcast updates."""
        while self._running:
            try:
                await asyncio.sleep(self.config.update_interval)
                if not self._running:
                    break

                status = await self._get_status()
                queue_status = await self._get_queue_status()

                await self._broadcast_update({
                    "type": "periodic_update",
                    "status": status,
                    "queue": queue_status,
                    "timestamp": datetime.now().isoformat(),
                })

                # Broadcast per-campaign metrics for running campaigns (from queue)
                if self.config.campaign_queue:
                    campaigns = await self._get_all_campaigns()
                    for campaign in campaigns.get("campaigns", []):
                        if campaign["status"] == "running":
                            metrics = await self._get_campaign_metrics_detailed(
                                campaign["campaign_id"]
                            )
                            await self._broadcast_update({
                                "type": "campaign_metrics",
                                "campaign_id": campaign["campaign_id"],
                                "data": metrics,
                                "timestamp": datetime.now().isoformat(),
                            })

                # ALSO: Broadcast metrics for any campaign with records in the store
                # This handles campaigns run directly via CLI (not through queue)
                if self.config.store_path:
                    try:
                        # Get run IDs with records, then close store before calling metrics
                        with self._readable_store() as store:
                            runs = store.query_runs()
                            run_ids = [
                                run.run_id
                                for run in runs
                                if run.status == "running"
                                or store.query_records(run_id=run.run_id)
                            ]

                        # Now query metrics for each run (each call opens its own connection)
                        for run_id in run_ids:
                            metrics = await self._get_campaign_metrics_detailed(run_id)
                            if metrics.get("records"):
                                await self._broadcast_update({
                                    "type": "campaign_metrics",
                                    "campaign_id": run_id,
                                    "data": metrics,
                                    "timestamp": datetime.now().isoformat(),
                                })
                    except Exception:
                        logger.debug("Store unavailable for broadcast", exc_info=True)

                # NEW: Broadcast pipeline events (mock for v1)
                await self._broadcast_update({
                    "type": "pipeline_event",
                    "stage": "s6_train",
                    "message": "compose joint system",
                    "level": "ok",
                    "timestamp": datetime.now().isoformat(),
                })
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in dashboard update loop")
                await asyncio.sleep(5)

    async def run(self) -> None:
        """Run the dashboard server (blocking)."""
        import uvicorn

        await self.start()
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
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
