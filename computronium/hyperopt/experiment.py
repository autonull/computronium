"""
Experiment Runner

Executes hyperparameter optimization trials and collects metrics.
"""

import contextlib
import io
import os
import shutil
import tempfile
import time
import traceback
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import numpy as np
import torch

from computronium.core.construction import construct_model
from computronium.core.logging import get_logger
from computronium.core.utils.device import get_device
from computronium.execution._guards import SafetyConfig
from computronium.execution._lifecycle import CheckpointManager, ExperimentArchiver
from computronium.execution.events import EventSink, NullEventSink
from computronium.execution.monitoring import InterferenceMonitor
from computronium.hyperopt.storage import HyperoptStorage
from computronium.tracking import ExperimentTracker
from computronium.utils import count_parameters

logger = get_logger()


__all__ = [
    "TrialRunner",
    "logger",
    "run_single_trial_task",
]


class TrialRunner:
    """Runs individual hyperparameter optimization trials."""

    def __init__(  # ruff: ignore[too-many-arguments]
        self,
        storage: HyperoptStorage | None = None,
        device: str = "auto",
        task: str = "shakespeare",
        quick_mode: bool = True,
        checkpoint_db_path: str | None = None,
        task_kwargs: dict | None = None,
        timeout: float = 3600.0,
        epochs: int = 3,
        event_sink: EventSink | None = None,
        *,
        model_cls: type | None = None,
    ):
        self.storage = storage or HyperoptStorage()
        self.checkpoint_db_path = checkpoint_db_path
        self.device = self._select_device(device)
        self.task_name = task
        self.quick_mode = quick_mode
        self.epochs = epochs
        self.task_kwargs = task_kwargs or {}
        self.timeout = timeout
        self.model_cls = model_cls
        self._events: EventSink = (
            event_sink if event_sink is not None else NullEventSink()
        )

        # Initialize Task abstraction
        self._setup_task()

    def _select_device(self, device: str) -> str:
        """Resolve 'auto' device selection."""
        if device == "auto":
            return str(get_device())
        return device

    def _setup_task(self):
        """Initialize and setup the task object via unified resolution."""
        from computronium.config.unified import DataConfig
        from computronium.domains.registry import resolve_task_from_data_config

        data_config = DataConfig(
            name=self.task_name,
            task=self.task_name,
            batch_size=64,
            val_batch_size=None,
            num_workers=4,
            seq_len=self.task_kwargs.get("seq_len", 64),
            augment=False,
            data_fraction=self.task_kwargs.get("data_fraction", 1.0),
            data_kwargs=self.task_kwargs,
        )

        self.task_obj = resolve_task_from_data_config(data_config, device=self.device)
        self.input_dim = self.task_obj.input_dim
        self.output_dim = self.task_obj.output_dim

    def run_trial(self, trial_id: int, pruning_callback=None) -> bool:
        """Run a single trial and record results."""
        trial = self.storage.get_trial(trial_id)
        if not trial:
            logger.warning("Trial %s not found", trial_id)
            return False

        self.storage.update_trial(trial_id, status="running")

        tracker = ExperimentTracker(
            project="computronium",
            name=f"trial_{trial_id}_{trial.model_name}",
            config=trial.config,
        )

        try:
            # 1. Create Model and Trainer
            model, trainer = self._create_model_and_trainer(trial, tracker)

            # 2. Setup Training (Schedule, Monitoring, Checkpointing)
            schedule, monitor, checkpoint_manager = self._setup_training_components(trial_id)

            # 3. Define Callbacks
            epoch_times = []
            start_time = time.time()

            on_epoch_end_callback = self._create_epoch_callback(
                trial_id, epoch_times, start_time, checkpoint_manager
            )
            wrapped_pruning_callback = self._create_pruning_callback(
                trial_id, pruning_callback, monitor
            )

            # 4. Execute Training Loop
            trajectory = self._execute_training_loop(
                schedule, monitor, trainer, trial_id, trial, on_epoch_end_callback, wrapped_pruning_callback
            )

            # 5. Finalize and Save
            if checkpoint_manager:
                checkpoint_manager.close()

            return self._finalize_trial(
                trial_id,
                trial,
                trajectory,
                monitor,
                epoch_times,
                model,
                trainer,
                config=trial.config,
            )

        except Exception as exc:  # broad: a failing trial must not stop the loop
            logger.warning("Trial %s failed: %s: %s", trial_id, type(exc).__name__, exc)
            self.storage.update_trial(trial_id, status="failed")
            return False
        finally:
            self._cleanup_trial_resources(tracker, monitor)

    def _setup_training_components(self, trial_id: int):
        """Setup schedule, monitor, and checkpoint manager."""
        from computronium.execution.training_dynamics import (
            ContinuousTrainingSchedule,
        )

        schedule = ContinuousTrainingSchedule(
            max_epochs=self.epochs, enable_pruning=True
        )
        monitor = (
            InterferenceMonitor(threshold_cpu=20.0, sustain_duration=5.0)
            if not self.quick_mode
            else None
        )
        checkpoint_manager = None
        if self.checkpoint_db_path:
            try:
                checkpoint_manager = CheckpointManager(
                    self.checkpoint_db_path, trial_id
                )
            except (OSError, ValueError, RuntimeError, TypeError) as e:
                logger.warning("Failed to init CheckpointManager: %s", e)

        return schedule, monitor, checkpoint_manager

    def _create_epoch_callback(self, trial_id: int, epoch_times: list, start_time: float, checkpoint_manager):
        """Create the epoch end callback."""
        def on_epoch_end_callback(epoch, metrics):
            # Timeout Check
            if time.time() - start_time > self.timeout:
                logger.warning(
                    "Trial %s exceeded timeout (%ss). Stopping.",
                    trial_id,
                    self.timeout,
                )
                raise TimeoutError(f"Trial exceeded {self.timeout}s limit.")

            self.storage.log_epoch(
                trial_id,
                epoch - 1,
                metrics["loss"],
                metrics.get("accuracy", 0.0),
                metrics.get("perplexity", 0.0),
                metrics["time"],
            )
            epoch_times.append(metrics["time"])
            if checkpoint_manager:
                checkpoint_manager.log_metric(epoch, 0, metrics)
            self._events.update_progress(epoch, self.epochs, metrics)

        return on_epoch_end_callback

    def _create_pruning_callback(self, trial_id: int, pruning_callback, monitor):
        """Create the wrapped pruning callback."""
        def wrapped_pruning_callback(tid, epoch, m):
            if pruning_callback and pruning_callback(tid, epoch, m):
                self.storage.update_trial(trial_id, status="pruned")
                if monitor:
                    monitor.stop()
                return True
            return False

        return wrapped_pruning_callback

    def _execute_training_loop(self, schedule, monitor, trainer, trial_id: int, trial, on_epoch_end_callback, wrapped_pruning_callback):
        """Execute the training loop."""
        if monitor:
            monitor.start()

        trajectory = schedule.train_with_checkpoints(
            trainer=trainer,
            trial_id=trial_id,
            model_name=trial.model_name,
            task_name=self.task_name,
            config=trial.config,
            optuna_trial=None,
            pruning_callback=wrapped_pruning_callback,
            on_epoch_end=on_epoch_end_callback,
        )

        if monitor:
            monitor.stop()

        return trajectory

    def _cleanup_trial_resources(self, tracker, monitor):
        """Cleanup resources after trial."""
        if monitor:
            monitor.stop()
        tracker.finish()

        # Robust Cleanup
        import gc

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def _create_model_and_trainer(self, trial, tracker):
        """Instantiate model and trainer based on trial config."""
        config = trial.config
        hidden_dim = config.get("hidden_dim", 128)
        num_layers = config.get("num_layers", 4)

        model_cls = self.model_cls
        if model_cls is None:
            raise ValueError(f"No model class provided for {trial.model_name!r}")

        # Build model
        model = self._build_model(model_cls, config, hidden_dim, num_layers, trial.model_name)

        # Extract training parameters
        lr = config.get("lr", 1e-3)
        beta = config.get("beta")
        steps = config.get("steps")

        # Prepare trainer kwargs
        trainer_kwargs = self._prepare_trainer_kwargs(config)
        self._resolve_optimizer(config, lr, model, trainer_kwargs)

        # Create safety config
        safety_config = SafetyConfig(
            max_grad_norm=config.get("grad_clip", 10.0),
            nan_check_frequency=10,
            max_nan_retries=3,
        )

        # Create trainer
        trainer = self._create_trainer(
            model, lr, steps, tracker, safety_config, trainer_kwargs
        )

        # Attach optimizer to model for models that expect it
        if hasattr(model, "optimizer"):
            model.optimizer = trainer.optimizer  # type: ignore[attr-defined]

        # Update model config with trial-specific parameters
        self._update_model_config(model, config_obj=getattr(model, "config", None), beta=beta, steps=steps)

        return model, trainer

    def _build_model(self, model_cls, config, hidden_dim, num_layers, model_name) -> torch.nn.Module:
        """Build the model using construct_model."""
        build_config = dict(config)
        build_config.setdefault("hidden_dim", hidden_dim)
        build_config.setdefault("num_layers", num_layers)
        build_config.setdefault("task_type", self.task_name)
        model = construct_model(
            model_cls,
            build_config,
            input_dim=self.input_dim,
            output_dim=self.output_dim,
            model_name=model_name,
        )
        return cast("torch.nn.Module", model).to(self.device)

    def _prepare_trainer_kwargs(self, config):
        """Prepare trainer kwargs by cleaning config."""
        trainer_kwargs = config.copy()
        for key in [
            "lr",
            "steps",
            "batches_per_epoch",
            "eval_batches",
            "model",
            "task",
            "tier",
            "job_id",
            "fold",
            "data_fraction",
            "is_verification",
            "verified_trial_id",
        ]:
            if key in trainer_kwargs:
                del trainer_kwargs[key]

        if "scheduler" in config:
            trainer_kwargs["scheduler_type"] = config["scheduler"]
            trainer_kwargs["scheduler_kwargs"] = config.get("scheduler_kwargs", {})

        return trainer_kwargs

    def _resolve_optimizer(self, config, lr, model, trainer_kwargs):
        """Resolve optimizer from string to instance."""
        optimizer_name = config.get("optimizer", "adam")
        if isinstance(optimizer_name, str):
            opt_cls = getattr(torch.optim, optimizer_name, torch.optim.Adam)
            optimizer = opt_cls(
                model.parameters(),
                lr=lr,
                weight_decay=float(config.get("weight_decay", 0.0)),
                **config.get("optimizer_kwargs", {}),
            )
            trainer_kwargs["optimizer"] = optimizer

    def _create_trainer(self, model, lr, steps, tracker, safety_config, trainer_kwargs):
        """Create the trainer."""
        return self.task_obj.create_trainer(
            model,
            lr=lr,
            steps=steps if steps else 20,
            batches_per_epoch=200 if not self.quick_mode else 5,
            eval_batches=50 if not self.quick_mode else 2,
            tracker=tracker,
            safety_config=safety_config,
            **trainer_kwargs,
        )

    def _update_model_config(self, model, config_obj, beta, steps):
        """Update model config with trial-specific parameters."""
        if beta is not None:
            if config_obj is not None and hasattr(config_obj, "beta"):
                try:
                    object.__setattr__(config_obj, "beta", beta)
                except (AttributeError, TypeError):
                    pass
            if hasattr(model, "beta"):
                if isinstance(model.beta, torch.Tensor):
                    model.beta.fill_(beta)
                else:
                    model.beta = beta

        if steps is not None and hasattr(model, "max_steps"):
            model.max_steps = int(steps)

    def _finalize_trial(
        self, trial_id, trial, trajectory, monitor, epoch_times, model, trainer, config
    ):
        """Process results, update storage, and archive artifacts."""
        self.storage.save_trajectory(trajectory)

        if trajectory.checkpoints and trajectory.checkpoints[-1].epoch < self.epochs:
            return False  # Pruned

        if monitor and monitor.check_interference():
            logger.warning("INTERFERENCE DETECTED: Rejecting trial results.")
            self.storage.update_trial(trial_id, status="failed")
            return False

        if not trajectory.checkpoints:
            logger.warning("No checkpoints found. Marking trial as failed.")
            self.storage.update_trial(trial_id, status="failed")
            return False

        last_ckpt = trajectory.checkpoints[-1]

        # Calculate avg iteration time
        divisor = (
            trainer.episodes_per_epoch
            if hasattr(trainer, "episodes_per_epoch")
            else (
                trainer.batches_per_epoch
                if hasattr(trainer, "batches_per_epoch")
                else 1
            )
        )
        avg_iter_time = np.mean(epoch_times) / divisor if epoch_times else 0.0

        # Store raw parameter count (not millions)
        param_count = count_parameters(model, trainable_only=False)

        self.storage.update_trial(
            trial_id,
            status="completed",
            epochs_completed=self.epochs,
            final_loss=last_ckpt.train_loss,
            accuracy=last_ckpt.val_acc,
            perplexity=last_ckpt.perplexity if last_ckpt.perplexity else 0.0,
            iteration_time=avg_iter_time,
            param_count=param_count,
        )

        if config.get("save_artifacts"):
            logger.info("Archiving artifacts...")
            archiver = ExperimentArchiver()
            final_metrics = {
                "loss": last_ckpt.train_loss,
                "accuracy": last_ckpt.val_acc,
                "perplexity": last_ckpt.perplexity,
            }
            archiver.archive_trial(
                trial_id=trial_id, model=model, config=config, metrics=final_metrics
            )

        logger.info("Trial %s completed successfully!", trial_id)
        return True


def run_single_trial_task(
    task: str,
    model_name: str,
    config: dict[str, object],
    storage_path: str | None = None,
    quick_mode: bool = True,
    verbose: bool = False,
    event_sink: EventSink | None = None,
) -> dict[str, float] | None:
    """
    Execute a single trial for a given task and model configuration.
    Wraps TrialRunner with storage and failure tracking.
    """
    temp_dir, db_path = _setup_storage(storage_path)
    storage: HyperoptStorage | None = None
    """
    Execute a single trial for a given task and model configuration.
    Wraps TrialRunner with storage and failure tracking.
    """
    temp_dir, db_path = _setup_storage(storage_path)
    storage = None

    try:
        storage = HyperoptStorage(str(db_path))

        # Create trial entry
        trial_id = storage.create_trial(model_name, config)

        # Log basic config info
        _log_trial_info(trial_id, task, model_name, config)

        # Extract task kwargs
        task_kwargs = _extract_task_kwargs(config)

        # Create runner
        timeout_raw = config.get("timeout", 3600.0)
        timeout_val: float = float(timeout_raw) if isinstance(timeout_raw, (int, float)) else 3600.0
        runner = TrialRunner(
            storage=storage,
            device="auto",
            task=task,
            quick_mode=quick_mode,
            checkpoint_db_path=str(db_path),
            task_kwargs=task_kwargs,
            timeout=timeout_val,
            event_sink=event_sink,
        )

        # Override epochs if present
        epochs_raw = config.get("epochs")
        if epochs_raw is not None:
            runner.epochs = int(epochs_raw)  # type: ignore[arg-type]

        # Run training
        success = _run_training(runner, trial_id, verbose)

        if success:
            return _collect_success_metrics(storage, trial_id, model_name, task, config)
        else:
            _handle_trial_failure(model_name, task, config, trial_id, verbose)
            return None

    except TimeoutError as e:
        logger.exception("Timeout Error")
        _sink_failure(model_name, task, config, "error", error=str(e))
        return None

    except Exception:  # broad: top-level executor safety net
        logger.exception("Execution Error")
        if verbose:
            traceback.print_exc()

        # Log exception failure
        _sink_failure(model_name, task, config, "error", error=traceback.format_exc())
        return None
    finally:
        _cleanup_trial(storage, temp_dir, verbose)


def _setup_storage(storage_path: str | None) -> tuple[str | None, Path]:
    """Setup temporary or persistent storage."""
    if storage_path is None:
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "worker_temp.db"
    else:
        temp_dir = None
        db_path = Path(storage_path)
    return temp_dir, db_path


def _log_trial_info(trial_id: int, task: str, model_name: str, config: dict) -> None:
    """Log trial information."""
    tier = config.get("tier", "unknown")
    epochs = config.get("epochs", "?")
    logger.info(
        "[Trial %s] Task: %s | Model: %s | Tier: %s | Epochs: %s",
        trial_id,
        task,
        model_name,
        tier,
        epochs,
    )


def _extract_task_kwargs(config: dict) -> dict:
    """Extract task-specific kwargs from config."""
    task_kwargs = {}
    if "fold" in config:
        task_kwargs["fold"] = config["fold"]
    if "data_fraction" in config:
        task_kwargs["data_fraction"] = config["data_fraction"]
    return task_kwargs


def _run_training(runner: TrialRunner, trial_id: int, verbose: bool) -> bool:
    """Run the training trial."""
    if verbose:
        return runner.run_trial(trial_id)
    else:
        # Suppress output but keep stderr for errors
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            return runner.run_trial(trial_id)


def _collect_success_metrics(
    storage: HyperoptStorage, trial_id: int, model_name: str, task: str, config: dict[str, object]
) -> dict[str, float]:
    """Collect metrics from successful trial."""
    trial = storage.get_trial(trial_id)
    if trial is None:
        raise RuntimeError(f"Trial {trial_id} not found after successful completion")
    metrics: dict[str, float] = {
        "trial_id": trial_id,
        "accuracy": trial.accuracy,
        "loss": trial.final_loss,
        "perplexity": trial.perplexity,
        "time": trial.iteration_time,
        "param_count": trial.param_count,
    }
    _sink_completed(model_name, task, config, metrics)
    return metrics


def _handle_trial_failure(
    model_name: str, task: str, config: dict, trial_id: int, verbose: bool
) -> None:
    """Handle trial failure."""
    if verbose:
        logger.warning("Trial %s returned success=False", trial_id)
    _sink_failure(model_name, task, config, "failed", trial_id=trial_id)


def _cleanup_trial(storage: HyperoptStorage | None, temp_dir: str | None, verbose: bool) -> None:
    """Cleanup trial resources."""
    if storage:
        storage.close()

    if verbose:
        logger.info("Cleaning up trial resources...")

    # Explicitly break references
    import gc
    import torch

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    if verbose:
        logger.info("Cleanup complete.")

    if temp_dir:
        shutil.rmtree(temp_dir)


def _sink_completed(
    model_name: str,
    task: str,
    config: dict[str, object],
    metrics: Mapping[str, object],
) -> None:
    """Persist a successful ExecutionEngine trial to the KnowledgeBase (best-effort).

    Separate from the probe-driver path so each success compounds into the
    knowledge layer regardless of which experiment framework produced it.
    """
    if os.environ.get("COMPUTRONIUM_RECORD_RESULTS", "1") == "0":
        return
    try:
        from computronium.experiment.result_sink import record_experiment_result

        seed_raw = config.get("seed")
        epochs_raw = config.get("epochs")
        record_experiment_result(
            model=model_name,
            task=task,
            config=config,
            metrics=dict(metrics),
            status="completed",
            seed=int(seed_raw) if seed_raw is not None else None,  # type: ignore[arg-type]
            epochs=int(epochs_raw) if epochs_raw is not None else None,  # type: ignore[arg-type]
            device="auto",
            extra={"source": "execution_engine"},
        )
    except Exception:  # pragma: no cover  # best-effort persistence
        logger.exception("result_sink failed for %s/%s", model_name, task)


def _sink_failure(
    model_name: str,
    task: str,
    config: dict[str, object],
    status: str,
    *,
    error: str = "",
    trial_id: int | None = None,
) -> None:
    """Persist a failed ExecutionEngine trial through the single result sink."""
    if os.environ.get("COMPUTRONIUM_RECORD_RESULTS", "1") == "0":
        return
    try:
        from computronium.experiment.result_sink import record_experiment_result

        extra: dict[str, object] = {
            "source": "execution_engine",
            "tier": config.get("tier", "unknown"),
        }
        if error:
            extra["error"] = error
        epochs_raw = config.get("epochs")
        job_id_raw = config.get("job_id")
        seed_val: int | None = int(job_id_raw) if job_id_raw is not None else (trial_id if trial_id is not None else None)  # type: ignore[arg-type]
        record_experiment_result(
            model=model_name,
            task=task,
            config=config,
            metrics={},
            status=status,
            seed=seed_val,
            epochs=int(epochs_raw) if epochs_raw is not None else None,  # type: ignore[arg-type]
            device="auto",
            extra=extra,
        )
    except Exception:  # pragma: no cover  # best-effort persistence
        logger.exception("result_sink failed for %s/%s", model_name, task)
