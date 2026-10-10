"""Environment Snapshots: uv lockfiles, container images, reproducibility (Phase E7).

Captures complete environment state for reproducible experiment execution.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- used for controlled CLI subprocess calls (git, uv, docker)
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PythonEnvironment:
    """Python environment snapshot."""

    python_version: str
    python_executable: str
    pip_packages: dict[str, str]
    uv_lock: str | None = None
    uv_lock_hash: str | None = None
    requirements_txt: str | None = None


@dataclass(frozen=True, slots=True)
class SystemEnvironment:
    """System environment snapshot."""

    platform: str
    platform_version: str
    architecture: str
    hostname: str
    cpu_count: int
    memory_gb: float
    gpu_info: list[dict[str, str]] = field(default_factory=list)
    cuda_version: str | None = None
    nvidia_driver_version: str | None = None


@dataclass(frozen=True, slots=True)
class GitEnvironment:
    """Git repository snapshot."""

    repo_root: str
    commit_sha: str
    branch: str
    is_dirty: bool
    untracked_files: list[str] = field(default_factory=list)
    remote_url: str | None = None


@dataclass(frozen=True, slots=True)
class ContainerEnvironment:
    """Container environment snapshot."""

    image_name: str
    image_id: str
    dockerfile_path: str | None = None
    dockerfile_content: str | None = None
    base_image: str | None = None
    build_args: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EnvironmentSnapshot:
    """Complete environment snapshot for reproducibility."""

    snapshot_id: str
    created_at: str
    python: PythonEnvironment
    system: SystemEnvironment
    git: GitEnvironment | None = None
    container: ContainerEnvironment | None = None
    environment_variables: dict[str, str] = field(default_factory=dict)
    custom_metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> EnvironmentSnapshot:
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(
            snapshot_id=data["snapshot_id"],
            created_at=data["created_at"],
            python=PythonEnvironment(**data["python"]),
            system=SystemEnvironment(**data["system"]),
            git=GitEnvironment(**data["git"]) if data.get("git") else None,
            container=ContainerEnvironment(**data["container"])
            if data.get("container")
            else None,
            environment_variables=data.get("environment_variables", {}),
            custom_metadata=data.get("custom_metadata", {}),
        )

    def save(self, path: Path) -> Path:
        """Save snapshot to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> EnvironmentSnapshot:
        """Load snapshot from file."""
        return cls.from_json(path.read_text(encoding="utf-8"))


class EnvironmentCapture:
    """Capture complete environment state."""

    def __init__(self, include_env_vars: bool = True, include_git: bool = True) -> None:
        self.include_env_vars = include_env_vars
        self.include_git = include_git

    def capture(self) -> EnvironmentSnapshot:
        """Capture current environment state."""
        snapshot_id = f"env_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        python_env = self._capture_python()
        system_env = self._capture_system()
        git_env = self._capture_git() if self.include_git else None
        env_vars = self._capture_env_vars() if self.include_env_vars else {}

        return EnvironmentSnapshot(
            snapshot_id=snapshot_id,
            created_at=datetime.now().isoformat(),
            python=python_env,
            system=system_env,
            git=git_env,
            environment_variables=env_vars,
        )

    def _capture_python(self) -> PythonEnvironment:
        """Capture Python environment."""
        # Get pip packages
        pip_packages = {}
        try:
            result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for pkg in json.loads(result.stdout):
                    pip_packages[pkg["name"]] = pkg["version"]
        except Exception as e:
            logger.debug(f"Failed to capture pip packages: {e}")

        # Get uv lock
        uv_lock = None
        uv_lock_hash = None
        uv_lock_path = Path("uv.lock")
        if uv_lock_path.exists():
            uv_lock = uv_lock_path.read_text(encoding="utf-8")
            import hashlib

            uv_lock_hash = hashlib.sha256(uv_lock.encode()).hexdigest()

        # Get requirements.txt if exists
        requirements_txt = None
        req_path = Path("requirements.txt")
        if req_path.exists():
            requirements_txt = req_path.read_text(encoding="utf-8")

        return PythonEnvironment(
            python_version=platform.python_version(),
            python_executable=sys.executable,
            pip_packages=pip_packages,
            uv_lock=uv_lock,
            uv_lock_hash=uv_lock_hash,
            requirements_txt=requirements_txt,
        )

    def _capture_system(self) -> SystemEnvironment:
        """Capture system environment."""
        # Get GPU info
        gpu_info = []
        cuda_version = None
        nvidia_driver_version = None

        try:
            import torch

            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    gpu_info.append({
                        "name": torch.cuda.get_device_name(i),
                        "memory_gb": round(
                            torch.cuda.get_device_properties(i).total_memory / 1e9, 2
                        ),
                        "capability": f"{torch.cuda.get_device_capability(i)[0]}.{torch.cuda.get_device_capability(i)[1]}",
                    })
                cuda_version = torch.version.cuda
        except Exception:
            pass

        try:
            result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
                ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                nvidia_driver_version = result.stdout.strip().split("\n")[0]
        except Exception:
            pass

        import psutil

        return SystemEnvironment(
            platform=platform.system(),
            platform_version=platform.version(),
            architecture=platform.machine(),
            hostname=platform.node(),
            cpu_count=os.cpu_count() or 0,
            memory_gb=round(psutil.virtual_memory().total / 1e9, 2),
            gpu_info=gpu_info,
            cuda_version=cuda_version,
            nvidia_driver_version=nvidia_driver_version,
        )

    def _capture_git(self) -> GitEnvironment | None:
        """Capture git repository state."""
        try:
            repo_root = self._find_git_root()
            if not repo_root:
                return None

            # Get commit SHA
            result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
                ["git", "rev-parse", "HEAD"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            commit_sha = result.stdout.strip() if result.returncode == 0 else "unknown"

            # Get branch
            result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            branch = result.stdout.strip() if result.returncode == 0 else "unknown"

            # Check if dirty
            result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
                ["git", "status", "--porcelain"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            is_dirty = bool(result.stdout.strip())
            untracked_files = (
                [
                    line[3:]
                    for line in result.stdout.strip().split("\n")
                    if line.startswith("??")
                ]
                if is_dirty
                else []
            )

            # Get remote URL
            result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
                ["git", "config", "--get", "remote.origin.url"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            remote_url = result.stdout.strip() if result.returncode == 0 else None

            return GitEnvironment(
                repo_root=repo_root,
                commit_sha=commit_sha,
                branch=branch,
                is_dirty=is_dirty,
                untracked_files=untracked_files,
                remote_url=remote_url,
            )
        except Exception as e:
            logger.debug(f"Failed to capture git state: {e}")
            return None

    def _find_git_root(self) -> str | None:
        """Find git repository root."""
        try:
            result = subprocess.run(  # ruff: ignore[start-process-with-partial-path, subprocess-without-shell-equals-true]
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _capture_env_vars(self) -> dict[str, str]:
        """Capture relevant environment variables."""
        relevant_prefixes = (
            "CUDA",
            "NVIDIA",
            "PYTHON",
            "PATH",
            "LD_LIBRARY_PATH",
            "CONDA",
            "VIRTUAL_ENV",
            "UV_",
            "PIP_",
            "TORCH",
        )
        env_vars = {}
        for key, value in os.environ.items():
            if any(key.startswith(prefix) for prefix in relevant_prefixes):
                env_vars[key] = value
        return env_vars


class ContainerManager:
    """Manage Docker containers for reproducible environments."""

    def __init__(self) -> None:
        self._client = None
        self._init_docker()

    def _init_docker(self) -> None:
        """Initialize Docker client."""
        try:
            import docker

            self._client = docker.from_env()
        except Exception as e:
            logger.debug(f"Docker not available: {e}")

    def is_available(self) -> bool:
        """Check if Docker is available."""
        return self._client is not None

    def build_image(
        self,
        dockerfile_path: str | Path,
        image_name: str,
        build_args: dict[str, str] | None = None,
        tag: str = "latest",
    ) -> ContainerEnvironment | None:
        """Build a Docker image and return environment info."""
        if not self.is_available():
            return None

        dockerfile_path = Path(dockerfile_path)
        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found: {dockerfile_path}")

        dockerfile_content = dockerfile_path.read_text(encoding="utf-8")

        # Extract base image
        base_image = None
        for line in dockerfile_content.split("\n"):
            line = line.strip()
            if line.startswith("FROM "):
                base_image = line[5:].split()[0]
                break

        full_name = f"{image_name}:{tag}"
        logger.info(f"Building Docker image: {full_name}")

        try:
            image, logs = self._client.images.build(  # type: ignore[union-attr]
                path=str(dockerfile_path.parent),
                dockerfile=dockerfile_path.name,
                tag=full_name,
                buildargs=build_args or {},
                rm=True,
            )

            return ContainerEnvironment(
                image_name=full_name,
                image_id=image.id or "",
                dockerfile_path=str(dockerfile_path),
                dockerfile_content=dockerfile_content,
                base_image=base_image,
                build_args=build_args or {},
            )
        except Exception as e:
            logger.exception(f"Failed to build Docker image: {e}")
            return None

    def save_image(self, image_name: str, output_path: Path) -> Path:
        """Save Docker image to tar archive."""
        if not self.is_available():
            raise RuntimeError("Docker not available")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            image = self._client.images.get(image_name)  # type: ignore[union-attr]
            with output_path.open("wb") as f:
                for chunk in image.save(named=True):
                    f.write(chunk)
            logger.info(f"Saved Docker image to {output_path}")
            return output_path
        except Exception as e:
            logger.exception(f"Failed to save Docker image: {e}")
            raise

    def load_image(self, input_path: Path) -> str | None:
        """Load Docker image from tar archive."""
        if not self.is_available():
            raise RuntimeError("Docker not available")

        try:
            with input_path.open("rb") as f:
                images = self._client.images.load(f)  # type: ignore[union-attr]
            if images:
                return images[0].id
            return None
        except Exception as e:
            logger.exception(f"Failed to load Docker image: {e}")
            return None


def create_environment_snapshot(
    output_path: Path | str,
    include_env_vars: bool = True,
    include_git: bool = True,
    include_container: bool = False,
    container_image: str | None = None,
) -> EnvironmentSnapshot:
    """Create and save a complete environment snapshot."""
    capture = EnvironmentCapture(
        include_env_vars=include_env_vars, include_git=include_git
    )
    snapshot = capture.capture()

    if include_container and container_image:
        manager = ContainerManager()
        if manager.is_available():
            try:
                container_env = ContainerEnvironment(
                    image_name=container_image,
                    image_id="",  # Would need to inspect
                )
                # This would need docker inspect to get full info
                snapshot = EnvironmentSnapshot(
                    snapshot_id=snapshot.snapshot_id,
                    created_at=snapshot.created_at,
                    python=snapshot.python,
                    system=snapshot.system,
                    git=snapshot.git,
                    container=container_env,
                    environment_variables=snapshot.environment_variables,
                    custom_metadata=snapshot.custom_metadata,
                )
            except Exception as e:
                logger.debug(f"Failed to capture container info: {e}")

    snapshot.save(Path(output_path))
    return snapshot


def verify_environment(snapshot_path: Path | str) -> dict[str, Any]:
    """Verify current environment matches a snapshot."""
    expected = EnvironmentSnapshot.load(Path(snapshot_path))
    actual = EnvironmentCapture().capture()

    mismatches = []

    # Compare Python packages
    for pkg, expected_version in expected.python.pip_packages.items():
        actual_version = actual.python.pip_packages.get(pkg)
        if actual_version != expected_version:
            mismatches.append({
                "type": "package",
                "package": pkg,
                "expected": expected_version,
                "actual": actual_version or "NOT INSTALLED",
            })

    # Check for extra packages
    for pkg in actual.python.pip_packages:
        if pkg not in expected.python.pip_packages:
            mismatches.append({
                "type": "extra_package",
                "package": pkg,
                "version": actual.python.pip_packages[pkg],
            })

    # Compare Python version
    if actual.python.python_version != expected.python.python_version:
        mismatches.append({
            "type": "python_version",
            "expected": expected.python.python_version,
            "actual": actual.python.python_version,
        })

    # Compare uv.lock
    if expected.python.uv_lock_hash and actual.python.uv_lock_hash:
        if expected.python.uv_lock_hash != actual.python.uv_lock_hash:
            mismatches.append({
                "type": "uv_lock",
                "expected_hash": expected.python.uv_lock_hash,
                "actual_hash": actual.python.uv_lock_hash,
            })

    # Compare git commit
    if expected.git and actual.git:
        if expected.git.commit_sha != actual.git.commit_sha:
            mismatches.append({
                "type": "git_commit",
                "expected": expected.git.commit_sha,
                "actual": actual.git.commit_sha,
            })

    return {
        "matches": len(mismatches) == 0,
        "mismatches": mismatches,
        "expected_snapshot_id": expected.snapshot_id,
        "actual_snapshot_id": actual.snapshot_id,
    }


__all__ = [
    "ContainerEnvironment",
    "ContainerManager",
    "EnvironmentCapture",
    "EnvironmentSnapshot",
    "GitEnvironment",
    "PythonEnvironment",
    "SystemEnvironment",
    "create_environment_snapshot",
    "verify_environment",
]
