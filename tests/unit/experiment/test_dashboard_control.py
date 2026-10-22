"""The control verbs, as an agent or a browser calls them (TODO70).

The dashboard's controls are real: they reach a run that lives in another
process, through the control plane. These tests call the endpoints over
HTTP — no browser — because the claim is that an agent can drive the system
as well as a reader can.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from computronium.experiment.execution.campaign_queue import CampaignQueue
from computronium.experiment.execution.control import (
    ControlPlane,
    RunStatus,
    control_plane_path,
)
from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)

if TYPE_CHECKING:
    from pathlib import Path


def _dashboard(tmp_path: Path, queue: CampaignQueue | None = None) -> WebDashboard:
    """A dashboard over a store that need not exist: the plane is beside it."""
    return WebDashboard(
        DashboardConfig(
            store_path=str(tmp_path / "experiment.duckdb"),
            campaign_queue=queue,
            enable_websockets=False,
        )
    )


def _plane(dashboard: WebDashboard) -> ControlPlane:
    """The plane the dashboard writes, read the way the run reads it."""
    return ControlPlane(control_plane_path(dashboard.config.store_path))


class TestControlEndpoint:
    """What the control bar polls, and what it may ask for."""

    def test_the_control_endpoint_carries_the_plane_and_the_machine(
        self, tmp_path: Path
    ) -> None:
        """Everything the bar shows is on this one payload.

        The plane says what the run has been asked to do; the machine says
        how busy it is. The run's own counters come from the same document.
        """
        dashboard = _dashboard(tmp_path)

        with TestClient(dashboard.app) as client:
            response = client.get("/api/control")

        assert response.status_code == 200
        body = response.json()
        assert body["control"]["paused"] is False
        assert body["control"]["revision"] == 0
        assert body["readable"] is True
        assert "cpu_percent" in body["machine"]
        assert body["machine"]["cpu_count"]

    def test_the_control_endpoint_reads_the_runs_own_counters(
        self, tmp_path: Path
    ) -> None:
        """The run publishes what it is doing, and the endpoint carries it."""
        dashboard = _dashboard(tmp_path)
        _plane(dashboard).write_status(
            RunStatus(run_id="r1", stage="s6_train", in_flight=3, cells_done=11)
        )

        with TestClient(dashboard.app) as client:
            body = client.get("/api/control").json()

        assert body["status"]["run_id"] == "r1"
        assert body["status"]["stage"] == "s6_train"
        assert body["status"]["in_flight"] == 3
        assert body["status"]["cells_done"] == 11

    def test_pause_reaches_the_plane_the_run_reads(self, tmp_path: Path) -> None:
        """The verb is not a picture of a verb: it lands on the document."""
        dashboard = _dashboard(tmp_path)

        with TestClient(dashboard.app) as client:
            response = client.post("/api/control", json={"paused": True})

        assert response.status_code == 200
        assert response.json()["control"]["paused"] is True
        assert _plane(dashboard).read().paused is True

    def test_a_step_releases_one_more_batch(self, tmp_path: Path) -> None:
        dashboard = _dashboard(tmp_path)

        with TestClient(dashboard.app) as client:
            client.post("/api/control", json={"step": True})
            body = client.post("/api/control", json={"step": True}).json()

        assert body["control"]["step_budget"] == 2

    def test_the_ceiling_is_a_setting_a_reader_can_move(self, tmp_path: Path) -> None:
        dashboard = _dashboard(tmp_path)

        with TestClient(dashboard.app) as client:
            body = client.post("/api/control", json={"max_workers": 8}).json()

        assert body["control"]["max_workers"] == 8
        assert _plane(dashboard).read().max_workers == 8

    def test_a_stale_revision_is_refused(self, tmp_path: Path) -> None:
        """Two pages driving one run must not overwrite each other."""
        dashboard = _dashboard(tmp_path)

        with TestClient(dashboard.app) as client:
            client.post("/api/control", json={"paused": True})
            response = client.post(
                "/api/control", json={"paused": False, "revision": 0}
            )

        assert response.status_code == 409
        assert "moved on" in response.json()["error"]
        assert _plane(dashboard).read().paused is True, "the stale write was applied"

    def test_a_corrupt_plane_is_reported_not_hidden(self, tmp_path: Path) -> None:
        """The dashboard says the plane could not be read rather than
        pretending the run is running.
        """
        dashboard = _dashboard(tmp_path)
        _plane(dashboard).path.write_text("{not json", encoding="utf-8")

        with TestClient(dashboard.app) as client:
            body = client.get("/api/control").json()

        assert body["readable"] is False
        assert body["error"]
        assert body["control"]["paused"] is False


class TestStartingARun:
    """From no configuration: the new-run form's other end."""

    def test_the_profiles_are_offered_as_data(self, tmp_path: Path) -> None:
        dashboard = _dashboard(tmp_path)

        with TestClient(dashboard.app) as client:
            body = client.get("/api/profiles").json()

        names = {profile["name"] for profile in body["profiles"]}
        assert {
            "demo",
            "quick-verify",
            "production-map",
            "maturation",
            "claim",
        } <= names
        demo = next(p for p in body["profiles"] if p["name"] == "demo")
        assert demo["stages"]
        assert demo["n_seeds"] >= 1
        assert demo["axes"]

    def test_the_axes_are_offered_as_data(self, tmp_path: Path) -> None:
        dashboard = _dashboard(tmp_path)

        with TestClient(dashboard.app) as client:
            body = client.get("/api/axes").json()

        axes = {axis["axis"] for axis in body["axes"]}
        assert axes == {
            "substrate",
            "geometry",
            "dynamics",
            "plasticity",
            "credit",
            "update",
        }
        credit = next(axis for axis in body["axes"] if axis["axis"] == "credit")
        assert credit["primitives"]

    def test_a_run_without_a_queue_is_refused_in_words(self, tmp_path: Path) -> None:
        """The dashboard must never appear to have a control it does not have.

        The answer is the command the reader could type instead.
        """
        dashboard = _dashboard(tmp_path, None)

        with TestClient(dashboard.app) as client:
            response = client.post("/api/runs", json={"profile": "demo"})

        assert response.status_code == 409
        body = response.json()
        assert body["started"] is False
        assert "queue" in body["error"]
        assert body["command"] == (
            f"uv run comp run demo --store {tmp_path / 'experiment.duckdb'}"
        )

    def test_a_run_with_a_queue_is_queued(self, tmp_path: Path) -> None:
        queue = CampaignQueue(max_concurrent=0)
        dashboard = _dashboard(tmp_path, queue)

        with TestClient(dashboard.app) as client:
            response = client.post(
                "/api/runs",
                json={"profile": "demo", "overrides": {"n_seeds": 2}},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["started"] is True
        assert body["campaign_id"]
        assert body["spec"]["n_seeds"] == 2
        queued = queue._queue[0]
        assert queued.spec.runs[0].overrides["n_seeds"] == 2

    def test_an_unknown_profile_is_refused(self, tmp_path: Path) -> None:
        dashboard = _dashboard(tmp_path, CampaignQueue(max_concurrent=0))

        with TestClient(dashboard.app) as client:
            response = client.post("/api/runs", json={"profile": "nonsense"})

        assert response.status_code == 409
        assert "unknown profile" in response.json()["error"]


class TestNarration:
    """The verbs are said in shape, not in figures."""

    def test_a_paused_run_is_narrated(self, tmp_path: Path) -> None:
        from computronium.experiment.execution.dashboard.narration import (
            control_sentence,
        )

        assert control_sentence({"paused": True}) == "The run is paused."
        assert control_sentence({"cancel": True}) == "The run has been stopped."
        assert control_sentence({"paused": False}) == ""
        assert control_sentence(None) == ""

    def test_the_sentence_says_no_figure(self) -> None:
        """The rule is the shape, never the number."""
        from computronium.experiment.execution.dashboard.narration import (
            control_sentence,
        )

        sentence = control_sentence({"paused": True, "max_workers": 4})
        assert "4" not in sentence
