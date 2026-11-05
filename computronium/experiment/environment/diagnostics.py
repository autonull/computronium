"""Environment diagnostics (doctor mode) for Computronium experiments.

Provides comprehensive environment validation and debugging information.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import sysconfig
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DiagnosticsResult:
    """Result of environment diagnostics."""

    python_ok: bool
    uv_ok: bool
    torch_ok: bool
    nvidia_ok: bool
    nvidia_info: dict
    cuda_available: bool
    cuda_info: dict
    computronium_imports_ok: bool
    dry_run_ok: bool
    errors: list[str]


def find_project_root(start: Path | None = None) -> Path | None:
    """Find project root by locating pyproject.toml."""
    current = start or Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return None


def check_nvidia_driver() -> tuple[bool, str, dict]:
    """Check NVIDIA driver and CUDA libraries."""
    info = {}
    # Check nvidia-smi
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        try:
            result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - nvidia_smi validated via shutil.which
                [
                    nvidia_smi,
                    "--query-gpu=name,driver_version,memory.total",
                    "--format=csv,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                info["nvidia_smi"] = result.stdout.strip()
            else:
                info["nvidia_smi_error"] = result.stderr.strip()
        except Exception as e:
            info["nvidia_smi_exception"] = str(e)
    else:
        info["nvidia_smi"] = "not found"

    # Check CUDA libraries
    cuda_libs = ["libcudart.so", "libcublas.so", "libcudnn.so"]
    for lib in cuda_libs:
        try:
            result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - ldconfig is system command
                ["ldconfig", "-p"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if lib in result.stdout:
                info[f"has_{lib}"] = True
            else:
                info[f"has_{lib}"] = False
        except Exception:
            info[f"has_{lib}"] = "unknown"

    ok = "nvidia_smi" in info and info["nvidia_smi"] != "not found"
    msg = "NVIDIA driver detected" if ok else "NVIDIA driver not found"
    return ok, msg, info


def check_python(min_version: tuple[int, int] = (3, 14)) -> tuple[bool, str]:
    """Check Python version meets minimum."""
    version = sys.version_info
    ok = version >= min_version
    msg = f"Python {version.major}.{version.minor}.{version.micro} (executable: {sys.executable})"
    if not ok:
        msg += f" - REQUIRES {min_version[0]}.{min_version[1]}+"
    return ok, msg


def check_uv() -> tuple[bool, str]:
    """Check uv is available."""
    uv_path = shutil.which("uv")
    if uv_path is None:
        return False, "uv not found in PATH"
    try:
        result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - uv_path validated via shutil.which
            [uv_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, f"uv error: {result.stderr.strip()}"
    except Exception as e:
        return False, f"uv check failed: {e}"


def check_torch(device: str = "auto") -> tuple[bool, str, bool, dict]:
    """Check torch is available and functional. Returns (ok, message, cuda_available, cuda_info)."""
    cuda_info = {}
    try:
        import torch
    except ImportError as e:
        return False, f"torch import failed: {e}", False, cuda_info
    except Exception as e:
        return False, f"torch import crashed: {e}", False, cuda_info

    cuda_available = False
    if device != "cpu":
        try:
            cuda_available = torch.cuda.is_available()
        except Exception as e:
            cuda_info["cuda_check_error"] = str(e)
            return False, f"torch.cuda.is_available() crashed: {e}", False, cuda_info

    if cuda_available:
        try:
            cuda_info["version"] = torch.version.cuda
            cuda_info["cudnn"] = torch.backends.cudnn.version()
            cuda_info["device_count"] = torch.cuda.device_count()
            cuda_info["devices"] = []
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                cuda_info["devices"].append({
                    "name": props.name,
                    "memory_gb": props.total_memory / 1e9,
                    "compute_capability": f"{props.major}.{props.minor}",
                })
        except Exception as e:
            cuda_info["query_error"] = str(e)

    # Test basic tensor ops on CPU first
    try:
        x = torch.tensor([1.0, 2.0])
        y = x * 2
        if y.tolist() != [2.0, 4.0]:
            return (
                False,
                "tensor ops produced unexpected result",
                cuda_available,
                cuda_info,
            )
    except Exception as e:
        return False, f"CPU tensor ops failed: {e}", cuda_available, cuda_info

    # Test CUDA tensor ops if available
    if cuda_available:
        try:
            x = torch.tensor([1.0, 2.0], device="cuda")
            y = x * 2
            if y.tolist() != [2.0, 4.0]:
                cuda_info["cuda_tensor_test"] = "failed"
            else:
                cuda_info["cuda_tensor_test"] = "passed"
        except Exception as e:
            cuda_info["cuda_tensor_test"] = f"failed: {e}"

    msg = f"Torch {torch.__version__}"
    if cuda_available:
        try:
            msg += f", CUDA {torch.version.cuda}, GPU: {torch.cuda.get_device_name(0)}"
        except Exception:
            msg += ", CUDA available (query failed)"
    elif device == "cpu":
        msg += ", CPU-only mode (CUDA skipped)"
    else:
        msg += ", CPU-only mode"

    return True, msg, cuda_available, cuda_info


def check_computronium_imports() -> tuple[bool, str, list[str]]:
    """Check critical computronium modules are importable."""
    required = [
        "computronium.core.logging",
        "computronium.domains._task_registry",
        "computronium.experiment.evidence.store",
        "computronium.experiment.evidence.store._models",
        "computronium.experiment.execution.pipeline._budget_constants",
        "computronium.experiment.kernel.evaluate",
        "computronium.experiment.kernel.search_space",
        "computronium.experiment.schema.axis",
        "computronium.experiment.schema.coordinate",
        "computronium.experiment.schema.run_spec",
        "computronium.ontology.system",
    ]
    failed = []
    for mod in required:
        try:
            __import__(mod)
        except Exception as e:
            failed.append(f"{mod}: {e}")

    ok = len(failed) == 0
    if ok:
        return True, f"All {len(required)} modules OK", []
    return False, f"{len(failed)} imports failed", failed


def check_dry_run(device: str = "cpu", hours: float = 0.001) -> tuple[bool, str, int]:
    """Run a minimal dry-run to verify the experiment pipeline works."""
    try:
        from computronium.experiment.simple_survey import run_simple_survey

        result = run_simple_survey(hours, fidelity="L0", dry_run=True, device=device)
    except Exception as e:
        return False, f"dry-run failed: {e}", 0
    else:
        n_cells = result.get("n", 0)
        if n_cells == 0:
            return False, "dry-run generated 0 cells - search space empty", 0
        return True, f"dry-run generated {n_cells} cells", n_cells


def run_diagnostics(
    device: str = "cpu",
    hours: float = 0.001,
    min_python: tuple[int, int] = (3, 14),
) -> DiagnosticsResult:
    """Run full environment diagnostics."""
    errors: list[str] = []

    python_ok, python_msg = check_python(min_python)
    if not python_ok:
        errors.append(python_msg)

    uv_ok, uv_msg = check_uv()
    if not uv_ok:
        errors.append(uv_msg)

    nvidia_ok, nvidia_msg, nvidia_info = check_nvidia_driver()
    if not nvidia_ok:
        errors.append(nvidia_msg)

    torch_ok, torch_msg, cuda_available, cuda_info = check_torch(device)
    if not torch_ok:
        errors.append(torch_msg)

    computronium_ok, computronium_msg, failed_imports = check_computronium_imports()
    if not computronium_ok:
        errors.append(computronium_msg)
        errors.extend(failed_imports)

    dry_run_ok, dry_run_msg, _ = check_dry_run(device, hours)
    if not dry_run_ok:
        errors.append(dry_run_msg)

    return DiagnosticsResult(
        python_ok=python_ok,
        uv_ok=uv_ok,
        torch_ok=torch_ok,
        nvidia_ok=nvidia_ok,
        nvidia_info=nvidia_info,
        cuda_available=cuda_available,
        cuda_info=cuda_info,
        computronium_imports_ok=computronium_ok,
        dry_run_ok=dry_run_ok,
        errors=errors,
    )


def print_diagnostics(result: DiagnosticsResult) -> None:
    """Print formatted diagnostics output."""
    print("🔍 Computronium Environment Diagnostics")
    print("=" * 60)

    print("\n📋 System:")
    print(f"  OS: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Platform: {platform.platform()}")
    print(f"  sysconfig: {sysconfig.get_platform()}")

    print("\n🐍 Python:")
    print(f"  {sys.version.split()[0]}")
    print(f"  Executable: {sys.executable}")

    print("\n📦 uv:")
    print(f"  {(result.uv_ok and '✅') or '❌'} {result.uv_ok}")

    print("\n🎮 NVIDIA Driver:")
    print(f"  {(result.nvidia_ok and '✅') or '❌'} {result.nvidia_ok}")
    if result.nvidia_info:
        print("  NVIDIA details:")
        for key, value in result.nvidia_info.items():
            print(f"    {key}: {value}")

    print("\n🔥 Torch:")
    print(f"  {(result.torch_ok and '✅') or '❌'} {result.torch_ok}")
    print(f"  CUDA available: {result.cuda_available}")
    if result.cuda_info:
        print("  CUDA details:")
        for key, value in result.cuda_info.items():
            print(f"    {key}: {value}")

    print("\n🧪 Computronium imports:")
    print(
        f"  {(result.computronium_imports_ok and '✅') or '❌'} {result.computronium_imports_ok}"
    )

    print("\n🧪 Dry-run test:")
    print(f"  {(result.dry_run_ok and '✅') or '❌'} {result.dry_run_ok}")

    if result.errors:
        print("\n❌ Errors:")
        for err in result.errors:
            print(f"  - {err}")

    print("\n" + "=" * 60)
    all_ok = all([
        result.python_ok,
        result.uv_ok,
        result.torch_ok,
        result.computronium_imports_ok,
        result.dry_run_ok,
    ])
    print(f"Overall: {'✅ PASS' if all_ok else '❌ FAIL'}")
    print("=" * 60)


def main() -> int:
    """CLI entry point for diagnostics."""
    result = run_diagnostics()
    print_diagnostics(result)
    return 0 if result.errors == [] else 1


if __name__ == "__main__":
    sys.exit(main())
