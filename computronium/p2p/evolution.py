"""
P2P Evolutionary Controller.

Manages the autonomous discovery loop using the DHT.
"""

import hashlib
import json
import os
import random
import threading
import time
from dataclasses import dataclass, field
from typing import cast

from computronium.core.logging import get_logger
from computronium.hyperopt.experiment import run_single_trial_task
from computronium.hyperopt.search_space import get_available_models, get_search_space
from computronium.p2p.dht import DHTNode
from computronium.p2p.state import load_state, save_state

__all__ = [
    "P2PEvolution",
    "get_config_hash",
    "logger",
]
logger = get_logger("P2PEvolution")


@dataclass(frozen=True, slots=True)
class _GlobalBest:
    """The mesh's best record as one iteration of the loop sees it.

    The zero value is "no global best", which is the state every field takes
    before the first discovery: empty config, ``-inf`` score, generation 0.
    """

    record: dict | None = None
    config: dict = field(default_factory=dict)
    score: float = -float("inf")
    model_name: str = "EqProp MLP"
    gen: int = 0
    parent_hash: str | None = None


def get_config_hash(config: dict) -> str:
    """Generate a hash for a configuration."""

    def _default(obj):
        if hasattr(obj, "item"):  # numpy scalar
            return obj.item()
        if hasattr(obj, "tolist"):  # numpy array
            return obj.tolist()
        return str(obj)

    # sort keys to ensure determinism
    s = json.dumps(config, sort_keys=True, default=_default)
    return hashlib.md5(s.encode()).hexdigest()  # ruff: ignore[hashlib-insecure-hash-function]


class P2PEvolution:
    def __init__(
        self,
        bootstrap_ip: str | None = None,
        bootstrap_port: int = 8468,
        discovery_mode: str = "quick",
        constraints: dict | None = None,
        task: str = "shakespeare",
    ):
        self.bootstrap_nodes = [(bootstrap_ip, bootstrap_port)] if bootstrap_ip else []
        self.dht: DHTNode | None = None
        self.discovery_mode = discovery_mode
        self.constraints = constraints or {}
        self.task = task

        self.running = False
        self.thread: threading.Thread | None = None

        # State
        self.local_best_config: dict | None = None
        self.local_best_score = -float("inf")
        self.manual_queue: list[dict] = []  # Manually injected genomes

        state = load_state()
        self.points = state.get("points", 0)
        self.jobs_done = state.get("jobs_done", 0)

        self.current_status = "Stopped"

        # Signals
        self.on_status_change = None
        self.on_log = None

    def _log(self, msg):
        logger.info(msg)
        if self.on_log:
            self.on_log(msg)

    def _update_status(self, status):
        self.current_status = status
        if self.on_status_change:
            self.on_status_change(status, self.points, self.jobs_done)

    def start(self, auto_nice=True):
        if self.running:
            return

        if auto_nice and hasattr(os, "nice"):
            try:
                os.nice(10)  # Lower priority
                self._log("Process priority lowered (Nice +10)")
            except (OSError, AttributeError) as e:
                self._log(f"Could not lower priority: {e}")

        if not self._start_dht():
            return

        self.running = True
        self.thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.thread.start()
        self._update_status("Starting P2P Mesh...")

    def _start_dht(self) -> bool:
        """Bind the DHT, retrying a handful of neighbouring ports.

        Returns False (having logged) when every attempt failed; the caller
        must not start the evolution loop without a mesh.
        """
        base_port = 8468 + random.randint(0, 1000)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
        for offset in range(10):
            local_port = base_port + offset
            try:
                self.dht = DHTNode(
                    port=local_port, bootstrap_nodes=self.bootstrap_nodes
                )
                self.dht.start()
            except Exception as e:  # broad: async/network best-effort
                self._log(f"Port {local_port} busy/failed, retrying... ({e})")
                time.sleep(0.5)
                continue
            self._log(f"DHT started on port {local_port}")
            return True
        self._log("Failed to start DHT after retries")
        return False

    def stop(self):
        self.running = False
        if self.dht:
            self.dht.stop()
        if self.thread:
            self.thread.join(timeout=2)
        self._update_status("Stopped")

    def inject_genome(self, config: dict):
        """Inject a manually designed genome into the evaluation queue."""
        self._log("💉 Injecting manual genome for evaluation...")
        self.manual_queue.append(config)

    def _verify_model(self, record: dict) -> bool:
        """
        Spot-check a model from the network to ensure accuracy is valid.
        Returns True if valid (or close enough), False otherwise.
        """
        config = record.get("config", {})
        claimed_score = record.get("score", 0.0)
        model_name = config.get("model_name", "EqProp MLP")

        self._log(f"🕵️ Verifying global best... (Claimed: {claimed_score:.4f})")
        self._update_status("Verifying Global Best...")

        # Run a quick evaluation
        # We might use fewer epochs for speed, but ideally we match the claimed effort
        # For now, just run same settings as discovery mode
        metrics = run_single_trial_task(
            task=self.task,
            model_name=model_name,
            config=config,
            storage_path=None,  # Don't pollute main DB with verifications
            quick_mode=(self.discovery_mode == "quick"),
        )

        if not metrics:
            self._log("Verification failed: Could not run model.")
            return False

        real_score = metrics.get("accuracy", 0.0)

        # Allow some variance (e.g. 5%)
        tolerance = 0.05
        if abs(real_score - claimed_score) > tolerance and real_score < claimed_score:
            self._log(
                f"[FAIL]  Verification FAILED! (Real: {real_score:.4f}"
                f" vs Claimed: {claimed_score:.4f})"
            )
            return False

        self._log(f"[OK]  Verification PASSED (Real: {real_score:.4f})")
        return True

    def _evolution_loop(self):
        self._log("Joined P2P Mesh network.")

        while self.running:
            try:
                best = self._fetch_global_best()
                action = self._choose_action(best)
                config, model_name, next_gen = self._build_genome(action, best)
                target_config = self._constrain_and_configure(config, model_name)
                self._evaluate(target_config, model_name, next_gen, best.score)
            except Exception as e:  # broad: process/network loop
                self._log(f"Evolution Loop Error: {e}")
                import traceback

                traceback.print_exc()
                time.sleep(5)

            # Rest
            if self.running:
                self._update_status("Resting...")
                time.sleep(2)

    def _require_dht(self) -> DHTNode:
        if self.dht is None:
            raise RuntimeError("mesh is not started")
        return self.dht

    def _fetch_global_best(self) -> _GlobalBest:
        self._update_status("Syncing with Mesh...")
        best_record = self._require_dht().get_best_model(self.task)

        if (
            best_record is not None
            and random.random() < 0.1  # ruff: ignore[suspicious-non-cryptographic-random-usage]
            and not self._verify_model(best_record)
        ):
            self._log("Ignoring invalid global best.")
            best_record = None

        if not best_record:
            self._log("No global best found. Will seed new...")
            return _GlobalBest()

        config = best_record.get("config", {})
        score = best_record.get("score", -float("inf"))
        gen = config.get("generation", 0)
        self._log(f"Found global best: {score:.4f} (Gen {gen})")
        return _GlobalBest(
            record=best_record,
            config=config,
            score=score,
            model_name=config.get("model_name", "EqProp MLP"),
            gen=gen,
            parent_hash=get_config_hash(config),
        )

    def _choose_action(self, best: _GlobalBest) -> str:
        if self.manual_queue:
            return "manual"
        rnd = random.random()  # ruff: ignore[suspicious-non-cryptographic-random-usage]
        if rnd < 0.05:
            return "new_arch"
        if (
            self.local_best_config
            and best.record
            and self.local_best_config.get("model_name") == best.model_name
            and rnd < 0.35
        ):
            return "crossover"
        return "mutate"

    def _build_genome(self, action: str, best: _GlobalBest) -> tuple[dict, str, int]:
        match action:
            case "manual":
                self._update_status("Evaluating Manual Design...")
                config = self.manual_queue.pop(0)
                model_name = config.get("model_name", best.model_name)
                # A manual genome with no generation is a new line or a fork of
                # the global best; an explicit one continues it.
                config.setdefault("generation", best.gen + 1)
                return config, model_name, config["generation"]
            case "new_arch":
                self._update_status("Exploring New Architecture...")
                model_name = random.choice(get_available_models())  # ruff: ignore[suspicious-non-cryptographic-random-usage]
                config = get_search_space(model_name).sample()
                config["model_name"] = model_name
                self._log(f"Selected new architecture: {model_name}")
                return config, model_name, 0
            case "crossover":
                local = self.local_best_config or {}
                self._update_status("Crossing Over Genomes...")
                space = get_search_space(best.model_name)
                config = space.crossover(best.config, local)
                config["model_name"] = best.model_name
                config = space.mutate(config, mutation_rate=0.1)
                local_gen = int(local.get("generation", 0))
                return config, best.model_name, max(best.gen, local_gen) + 1
            case _:
                return self._mutate_genome(best)

    def _mutate_genome(self, best: _GlobalBest) -> tuple[dict, str, int]:
        self._update_status("Mutating Genome...")
        parent_config = best.config
        parent_model = best.model_name
        parent_gen = best.gen
        parent_hash = best.parent_hash

        if not best.record:  # Bootstrap
            space = get_search_space(best.model_name)
            parent_config = space.sample()
            parent_config["model_name"] = best.model_name
            parent_gen = 0
            parent_hash = None
        elif self.local_best_config and random.random() < 0.3:  # ruff: ignore[suspicious-non-cryptographic-random-usage]
            parent_config = self.local_best_config
            parent_model = parent_config.get("model_name", "EqProp MLP")
            parent_gen = parent_config.get("generation", 0)
            parent_hash = get_config_hash(parent_config)

        config = get_search_space(parent_model).mutate(parent_config)
        config["model_name"] = parent_model
        config["generation"] = parent_gen + 1
        if parent_hash:
            config["parent_id"] = parent_hash
        return config, parent_model, parent_gen + 1

    def _constrain_and_configure(self, config: dict, model_name: str) -> dict:
        target = config
        target["model_name"] = model_name

        if self.constraints:
            space = get_search_space(model_name).apply_constraints(self.constraints)
            target = space.mutate(target, mutation_rate=0.0)
            self._clamp(target)

        if self.discovery_mode == "quick":
            target["epochs"] = 1
            if "steps" in target:
                target["steps"] = min(cast("int", target["steps"]), 15)
        elif self.discovery_mode == "deep":
            target["epochs"] = 5

        return target

    def _clamp(self, config: dict) -> None:
        """Bound the keys ``space.mutate`` does not enforce on existing values."""
        for config_key, limit in (
            ("hidden_dim", "max_hidden"),
            ("num_layers", "max_layers"),
            ("steps", "max_steps"),
        ):
            bound = self.constraints.get(limit)
            if bound is not None and config_key in config:
                config[config_key] = min(int(config[config_key]), int(bound))

    def _evaluate(
        self, target_config: dict, model_name: str, next_gen: int, global_best: float
    ) -> None:
        self._update_status(f"Evaluating: {model_name} (Gen {next_gen})")
        metrics = run_single_trial_task(
            task=self.task,
            model_name=model_name,
            config=target_config,
            storage_path="results/hyperopt.db",
            quick_mode=(self.discovery_mode == "quick"),
        )

        if not metrics:
            self._log("Evaluation failed.")
            return

        acc = metrics.get("accuracy", 0.0)
        self.jobs_done += 1
        self.points += 5
        save_state(self.points, self.jobs_done)
        self._log(f"Eval complete: {acc:.4f} (Global Best: {global_best:.4f})")

        if acc > self.local_best_score:
            self.local_best_score = acc
            self.local_best_config = target_config
            self._log(f"New Local Best! ({acc:.4f})")

        if acc > global_best:
            self._update_status("Publishing Discovery...")
            self._require_dht().publish_best_model(self.task, target_config, acc)
            self.points += 50
            save_state(self.points, self.jobs_done)
            self._log(f"[SUCCESS]  New Global Best Discovered! ({acc:.4f})")
