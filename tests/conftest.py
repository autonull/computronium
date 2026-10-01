"""Shared test fixtures and configuration.

Determinism: numeric assertions must seed locally
(``torch.manual_seed`` or an explicit ``torch.Generator``), because the
suite runs under ``-n 4`` where each worker holds its own global RNG
stream, so an unseeded failure cannot be reproduced from its inputs.
``tests/property/test_rng_seed_lock.py`` ratchets this; shape-only tests
are exempt because a draw's values cannot change its shape.

Walltime: a test that outruns the global timeout declares a budget next to
itself, and the end-of-run walltime report is what notices a test that grew
into needing one — the discovery half of the policy in
``tests/test_timeout_marker_policy.py``, which can census a marker but
cannot see the absence of one.

The suite's thread count is pinned in the root ``conftest.py``, not here: it
has to be set before torch is imported, and this module imports torch. It
used to be set here anyway, below the import, where it did nothing.
``tests/property/test_determinism_thread_lock.py`` holds the pin.
"""

import logging
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
import torch
from torch import nn

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

# Hard dependencies — no mock stubs needed
# computronium.acceleration checks for cupy

sys.modules["cupy"] = MagicMock()

# Probe sibling imports: one canonical anchor for the whole suite
# (T21.3A.8) — per-file inserts deleted from tests and probe scripts.
_REPO_ROOT = Path(__file__).resolve().parents[1]
for _scripts_dir in ("scripts", "scripts/probes"):
    _probe_path = _REPO_ROOT / _scripts_dir
    if _probe_path.is_dir() and str(_probe_path) not in sys.path:
        sys.path.insert(0, str(_probe_path))


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--capture-screenshots",
        action="store_true",
        default=False,
        help="Enable screenshot capture for visual verification",
    )
    parser.addoption(
        "--walltime-report",
        metavar="PATH",
        default=None,
        help="Write every test's measured call seconds to PATH as a markdown table.",
    )


def pytest_configure(config: Any) -> None:
    config.addinivalue_line(
        "markers", "screenshots: mark test as capturing screenshots"
    )


#: A test whose call phase runs longer than this with no declared budget is
#: reported at the end of the run. Five seconds is roughly where a test stops
#: being a check and becomes a cost: 4,000 tests at 0.05 s is a fast lane, and
#: the point of the threshold is to keep the report short enough to be read.
WALLTIME_DISCOVERY_S = 5.0

#: nodeid -> measured call seconds, for tests carrying no ``timeout`` marker.
#: A test that declares a budget has already made the decision, so it is not a
#: discovery candidate however long it runs.
_UNDECLARED_WALLTIME: dict[str, float] = {}


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call" or "timeout" in report.keywords:
        return
    _UNDECLARED_WALLTIME[report.nodeid] = max(
        _UNDECLARED_WALLTIME.get(report.nodeid, 0.0), report.duration
    )


def _walltime_section(terminalreporter: Any) -> list[str]:
    """The undeclared tests that ran long, as a terminal-summary section.

    Reported and not failed. A test crossing the threshold on a loaded machine
    is not a policy violation — it is the policy working — and failing the run
    over it would make the report something people suppress, which is the
    outcome this file exists to prevent. The remedy for a row is a
    ``@pytest.mark.timeout`` next to the test, recorded in
    ``tests/test_timeout_marker_policy.py``.
    """
    slow = sorted(
        (seconds, nodeid)
        for nodeid, seconds in _UNDECLARED_WALLTIME.items()
        if seconds > WALLTIME_DISCOVERY_S
    )
    if not slow:
        return []
    lines = [
        f"tests over {WALLTIME_DISCOVERY_S}s with no @pytest.mark.timeout budget:",
        "",
    ]
    lines += [
        f"  {seconds:7.2f}s  {nodeid}  →  @pytest.mark.timeout({_budget_for(seconds)})"
        for seconds, nodeid in reversed(slow)
    ]
    lines += [
        "",
        "Add the marker next to the test and the row to KNOWN_LONG "
        "(tests/test_timeout_marker_policy.py).",
    ]
    return lines


#: Budgets are drawn from this ladder, which is the vocabulary
#: :data:`KNOWN_LONG` already speaks. A number computed to three significant
#: figures off one measurement reads as precision the measurement does not have
#: — and `3197` is what four times of headroom plus a floor produces.
_WALLTIME_LADDER = (300, 600, 900, 1200, 1800, 3600)

#: Headroom over the measurement, for machine speed and full-suite load. The
#: policy exists because a 120 s kill is indistinguishable from a flake; a
#: budget derived from one measurement with no headroom reintroduces exactly
#: that, with the same test and a busier machine.
_WALLTIME_HEADROOM = 4


def _budget_for(seconds: float) -> int:
    """The smallest ladder rung that leaves :data:`_WALLTIME_HEADROOM` over."""
    needed = _WALLTIME_HEADROOM * seconds
    return next(
        (rung for rung in _WALLTIME_LADDER if rung >= needed), _WALLTIME_LADDER[-1]
    )


def _write_walltime_report(path: str) -> None:
    """Every test's measured call seconds, slowest first.

    Written on request rather than every run because it is a snapshot of one
    machine on one day: the file that consumes it is a decision, and decisions
    are made from a reading, not from whatever the last run happened to say.
    """
    rows = sorted(
        ((seconds, nodeid) for nodeid, seconds in _UNDECLARED_WALLTIME.items()),
        reverse=True,
    )
    lines = [
        "# Measured test walltime",
        "",
        f"{len(rows)} tests with no declared budget, slowest first.",
        "Regenerate with `pytest --walltime-report=<path>`.",
        "",
        "| seconds | nodeid |",
        "|---:|---|",
    ]
    lines += [f"| {seconds:.2f} | `{nodeid}` |" for seconds, nodeid in rows]
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def pytest_terminal_summary(
    terminalreporter: Any, exitstatus: int, config: Any
) -> None:
    if hasattr(config, "workerinput"):
        return
    report = config.getoption("--walltime-report", default=None)
    if report:
        _write_walltime_report(report)
    section = _walltime_section(terminalreporter)
    if section:
        terminalreporter.write_sep("=", "walltime discovery", red=True)
        terminalreporter.write_line("\n".join(section))


@pytest.fixture
def capture_screenshots(request: Any) -> bool:
    """Check if screenshot capture is enabled."""
    return request.config.getoption("--capture-screenshots")


def lm_train_step(
    model: nn.Module, input_ids: torch.Tensor, target_ids: torch.Tensor | None = None
) -> dict[str, float]:
    """Route a TileLM-style token-id training step through ``dispatch_train_step``.

    TileLM exposes no self-owned learning rule (``train_step`` raises
    ``NotImplementedError``), so the dispatcher's BPTT fallback owns the step.
    This mirrors the historical standalone ``train_step`` contract.
    """
    from computronium.core.trainer import dispatch_train_step

    if target_ids is None:
        target_ids = input_ids.clone()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

    def bptt_step(x: torch.Tensor, y: torch.Tensor) -> dict[str, object]:
        logits = model(x)
        loss = model.compute_loss(logits, y)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        with torch.no_grad():
            perplexity = torch.exp(torch.clamp(loss, max=80)).item()
        return {"loss": loss.item(), "perplexity": perplexity}

    return dispatch_train_step(
        model=cast("nn.Module", model),
        x=input_ids,
        y=target_ids,
        adapt_input=lambda x: x,
        bptt_step=bptt_step,
    )


# --- Shared Model Fixtures ---


class SimpleMLP(nn.Module):
    """Minimal 2-layer MLP for eqprop tests."""

    def __init__(self, input_dim: int = 10, hidden_dim: int = 20, output_dim: int = 5):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = x
        for layer in self.layers:
            h = layer(h)
        return h

    def transition_modules(self) -> list[nn.Module]:
        """Return linear layers as transition modules for settling."""
        return [m for m in self.layers if isinstance(m, nn.Linear)]


@pytest.fixture
def simple_mlp() -> SimpleMLP:
    return SimpleMLP()


@pytest.fixture
def sample_batch() -> tuple[torch.Tensor, torch.Tensor]:
    x = torch.randn(4, 10)
    y = torch.randint(0, 5, (4,))
    return x, y


def pytest_unconfigure(config: object) -> None:
    """Clean up test artifacts after session ends."""
    kb_tmp = Path(tempfile.gettempdir()) / "computronium-knowledgebase.json"
    if kb_tmp.exists():
        kb_tmp.unlink()
    kb_tmp_dir = Path(tempfile.gettempdir()) / "computronium_kb"
    if kb_tmp_dir.exists():
        shutil.rmtree(kb_tmp_dir, ignore_errors=True)
    cwd_kb = Path.cwd() / "knowledgebase.json"
    if cwd_kb.exists():
        cwd_kb.unlink()


def pytest_collection_modifyitems(config: object, items: list[pytest.Item]) -> None:
    """Apply GPU-marked skips when CUDA is unavailable.

    Any test carrying ``gpu_only`` is skipped on CPU-only machines; ``gpu``
    tests run on whatever device is present (they should be device-agnostic).

    Also stamps ``demo`` on every test under a ``test_demo_*.py`` module and on
    the gallery figure lock. The demos train networks and re-render figures, so
    their declared budgets sum to hours; they are artifact producers, not
    correctness checks, and the default gate must not pay for them. Marking them
    here rather than per file keeps a newly added demo out of the gate by
    construction. ``pytest -m demo`` re-pins the gallery; the manifest drift
    lock is what keeps them honest in between, and it is marked here so the demo
    gate is one selection.
    """
    demo = pytest.mark.demo
    for item in items:
        name = item.path.name
        if name.startswith("test_demo_") or name == "test_gallery_lock.py":
            item.add_marker(demo)
        if not torch.cuda.is_available() and "gpu_only" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="CUDA not available"))


# --- E.2 Shared Fixtures (test reorg) ---


@pytest.fixture(scope="session")
def synthetic_classification() -> tuple[torch.Tensor, torch.Tensor]:
    """Deterministic synthetic classification data for all fast tests."""
    torch.manual_seed(42)
    X = torch.randn(200, 64)
    y = (X.sum(dim=1) > 0).long() % 10
    return X, y


@pytest.fixture
def mnist_quick_task():
    """MNIST task in quick_mode (small subset, no download).

    Returns a VisionTask configured for quick test runs.
    """
    from computronium.tasks.vision import VisionTask

    return VisionTask("mnist", quick_mode=True)


@pytest.fixture
def eqprop_model():
    """Minimal native_eqprop_mlp for settling/contrastive tests."""
    from computronium.models.native.eqprop_native import native_eqprop_mlp

    return native_eqprop_mlp(
        input_dim=64,
        hidden_dim=32,
        output_dim=10,
        num_layers=1,
        beta=0.5,
        settle_steps=5,
    )


# --- Sprint 4.3.4 Synthetic Fixtures (zero I/O, zero download) ---


_CUDA_PRESENT = torch.cuda.is_available()


@pytest.fixture
def device(request: pytest.FixtureRequest) -> str:
    """Return 'cuda' if available, else 'cpu'.

    Persistent CUDA is avoided; tests that need a live GPU should use the
    ``gpu`` / ``gpu_only`` markers and place tensors on the returned device.

    ``cpu_only`` forces CPU, and it forces it here rather than in each test:
    a declared marker that nothing reads is not a marker. TileGeometry trips
    a CUDA device-side assert, and the poisoned context makes every later
    CUDA call in that worker raise -- so one marked test that ignored its own
    marker took 30 further tests down with it.
    """
    if request.node.get_closest_marker("cpu_only") is not None:
        return "cpu"
    return "cuda" if _CUDA_PRESENT else "cpu"


@pytest.fixture(scope="session")
def cuda_available() -> bool:
    """Whether CUDA is available to tests."""
    return torch.cuda.is_available()


@pytest.fixture
def synthetic_batch() -> tuple[torch.Tensor, torch.Tensor]:
    """A small deterministic batch (x, y) for fast feedforward tests."""
    torch.manual_seed(0)
    x = torch.randn(8, 64)
    y = torch.randint(0, 10, (8,))
    return x, y


@pytest.fixture(scope="session")
def synthetic_vision_task() -> tuple[torch.Tensor, torch.Tensor]:
    """Deterministic image-shaped classification tensors (no MNIST download).

    Returns (images, labels) where images are (N, 1, 16, 16). Tests that need a
    real VisionTask loader should use tests/slow/ instead.
    """
    torch.manual_seed(1)
    n = 64
    images = torch.randn(n, 1, 16, 16)
    # Inject a weak spatial signal so the task is learnable.
    images += (images.mean(dim=(2, 3), keepdim=True) > 0).float() * 0.5
    labels = (images.mean(dim=(2, 3)).squeeze(1) > 0).long() % 10
    return images, labels


@pytest.fixture(scope="session")
def synthetic_lm_task() -> tuple[torch.Tensor, torch.Tensor]:
    """Deterministic token-sequence batch for LM tests (no download).

    Returns (input_ids, target_ids) of shape (N, seq_len) over a small vocab.
    """
    torch.manual_seed(2)
    seq_len = 24
    vocab_size = 256
    n = 8
    ids = torch.randint(1, vocab_size, (n, seq_len))
    input_ids = ids[:, :-1]
    target_ids = ids[:, 1:]
    return input_ids, target_ids


# --- Sprint 1.1 GPU Fixtures (session-scoped, placed on CUDA) ---


@pytest.fixture(scope="session")
def gpu_device() -> str:
    """CUDA device for GPU tests (raises if CUDA unavailable)."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA not available", allow_module_level=False)
    return "cuda"


@pytest.fixture(scope="session")
def synthetic_batch_gpu(gpu_device: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Deterministic (x, y) batch on CUDA for GPU-accelerated tests."""
    torch.manual_seed(0)
    x = torch.randn(128, 64, device=gpu_device)
    y = torch.randint(0, 10, (128,), device=gpu_device)
    return x, y


@pytest.fixture(scope="session")
def synthetic_vision_task_gpu(gpu_device: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Deterministic image-shaped classification tensors on CUDA."""
    torch.manual_seed(1)
    n = 128
    images = torch.randn(n, 1, 16, 16, device=gpu_device)
    images += (images.mean(dim=(2, 3), keepdim=True) > 0).float() * 0.5
    labels = (images.mean(dim=(2, 3)).squeeze(1) > 0).long() % 10
    return images, labels


@pytest.fixture(scope="session")
def synthetic_lm_task_gpu(gpu_device: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Deterministic token-sequence batch on CUDA for LM tests."""
    torch.manual_seed(2)
    seq_len = 24
    vocab_size = 256
    n = 128
    ids = torch.randint(1, vocab_size, (n, seq_len), device=gpu_device)
    return ids[:, :-1], ids[:, 1:]
