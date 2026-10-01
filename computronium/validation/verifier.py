"""Verification suite for validation tracks (post-pillar cleanup)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from computronium.core.logging import get_logger
from computronium.utils import seed_everything

from .notebook import VerificationNotebook
from .tracks import track_registry

if TYPE_CHECKING:
    from .notebook import TrackResult

logger = get_logger()


class Verifier:
    """Verification suite for all research tracks.

    Runs validation tracks with configurable evidence levels.
    Knowledge-base recording removed (was pillar-dependent).
    """

    def __init__(
        self,
        quick_mode: bool = False,
        intermediate_mode: bool = False,
        seed: int = 42,
        output_dir: str | None = None,
    ):
        self.quick_mode = quick_mode
        self.intermediate_mode = intermediate_mode
        self.seed = seed
        self.notebook = VerificationNotebook()

        if output_dir is None:
            self.output_dir = Path("results")
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        seed_everything(seed)

        if quick_mode:
            self.epochs = 5
            self.n_samples = 200
            self.n_seeds = 1
            self.evidence_level = "smoke"
        elif intermediate_mode:
            self.epochs = 50
            self.n_samples = 5000
            self.n_seeds = 3
            self.evidence_level = "intermediate"
        else:
            self.epochs = 100
            self.n_samples = 10000
            self.n_seeds = 5
            self.evidence_level = "full"

        self.tracks = {}
        self._load_tracks()

    def _load_tracks(self):
        for tid, func in track_registry.ALL_TRACKS.items():
            name = func.__doc__.split("\n")[0] if func.__doc__ else func.__name__
            if ":" in name and "Track" in name.split(":")[0]:
                name = name.split(":", 1)[1].strip()
            self.tracks[tid] = (name, func)

    def print_header(self):
        evidence_labels = {
            "smoke": "[TEST]  Smoke Test (mechanics only)",
            "intermediate": "[DATA]  Intermediate (directional)",
            "full": "[OK]  Full Validation (statistically significant)",
        }
        mode_name = (
            "Quick"
            if self.quick_mode
            else ("Intermediate" if self.intermediate_mode else "Full")
        )
        mode_icon = (
            "[FAST] "
            if self.quick_mode
            else ("[DATA] " if self.intermediate_mode else "[LAB] ")
        )

        logger.info("=" * 70)
        logger.info("       COMPUTRONIUM VERIFICATION SUITE")
        logger.info("=" * 70)
        logger.info("\n[CONFIG]  Configuration:")
        logger.info("   Seed: %s", self.seed)
        logger.info("   Mode: %s %s", mode_icon, mode_name)
        logger.info("   Evidence: %s", evidence_labels[self.evidence_level])
        logger.info("   Epochs: %s", self.epochs)
        logger.info("   Samples: %s", self.n_samples)
        logger.info("   Seeds: %s", self.n_seeds)
        logger.info("   Tracks: %s", len(self.tracks))
        logger.info("=" * 70)

    def evaluate_robustness(self, track_fn, n_seeds: int = 3) -> dict:
        """Run a track function multiple times with different seeds."""
        scores = []
        metrics_list = []

        run_count = self.n_seeds
        if self.n_seeds == 3 and not self.quick_mode:
            run_count = n_seeds

        logger.info("      Running robustness check (%s seeds)...", run_count)

        for i in range(run_count):
            seed = self.seed + i * 100

            seed_everything(seed)

            try:
                score, metrics = track_fn()
                scores.append(score)
                metrics_list.append(metrics)
            except (RuntimeError, ValueError, TypeError, KeyError) as e:
                logger.warning("        Seed %s: Failed (%s)", seed, e)
                import traceback

                traceback.print_exc()
                scores.append(0)
                metrics_list.append({})

        mean_score = np.mean(scores)
        std_score = np.std(scores) if len(scores) > 1 else 0.0

        n = len(scores)
        se = std_score / np.sqrt(n) if n > 1 else 0.0
        ci_95 = 1.96 * se

        agg_metrics = {}
        if metrics_list:
            keys = metrics_list[0].keys()
            for k in keys:
                vals = [
                    m[k]
                    for m in metrics_list
                    if k in m and isinstance(m[k], (int, float))
                ]
                if vals:
                    m_mean = np.mean(vals)
                    m_std = np.std(vals) if len(vals) > 1 else 0.0
                    m_se = m_std / np.sqrt(len(vals)) if len(vals) > 1 else 0.0
                    m_ci = 1.96 * m_se
                    agg_metrics[f"{k}_mean"] = m_mean
                    agg_metrics[f"{k}_std"] = m_std
                    agg_metrics[f"{k}_ci95"] = m_ci

        return {
            "mean_score": mean_score,
            "std_score": std_score,
            "ci_95": ci_95,
            "metrics": agg_metrics,
            "all_scores": scores,
        }

    def run_tracks(
        self, track_ids: list[int] | None = None, parallel: bool = False
    ) -> dict[int, TrackResult]:
        """Run specified tracks (or all if None)."""
        self.print_header()
        self.notebook.add_header(self.seed)

        if track_ids is None:
            track_ids = list(self.tracks.keys())

        if (self.intermediate_mode or (not self.quick_mode)) and 0 not in track_ids:
            logger.info("Running Track 0 (Framework Validation) automatically...")
            track_ids = [0] + track_ids

        results = {}
        start_time = time.time()

        def _execute_track(tid: int):
            if tid not in self.tracks:
                return tid, None, f"Unknown track: {tid}"
            _name, method = self.tracks[tid]
            try:
                result = method(self)
                return tid, result, None
            except (RuntimeError, ValueError, TypeError, KeyError) as e:
                import traceback

                return tid, None, f"Failed: {e}\n{traceback.format_exc()}"

        if parallel and len(track_ids) > 1:
            import concurrent.futures

            logger.info("Running %s tracks in parallel...", len(track_ids))
            max_workers = min(len(track_ids), 4)
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                future_to_track = {
                    executor.submit(_execute_track, tid): tid for tid in track_ids
                }

                completed = 0
                for future in concurrent.futures.as_completed(future_to_track):
                    tid, result, error = future.result()

                    if error:
                        logger.error("Track %s error: %s", tid, error)
                    elif result:
                        results[tid] = result
                        self.notebook.add_track_result(result)

                        icon = {
                            "pass": "[OK] ",
                            "fail": "[FAIL] ",
                            "partial": "[WARN] ",
                            "stub": "[TODO] ",
                        }.get(result.status, "?")
                        name, _ = self.tracks[tid]
                        logger.info(
                            "%s Track %s: %s - %s (%.0f/100)",
                            icon,
                            tid,
                            name,
                            result.status.upper(),
                            result.score,
                        )

                    completed += 1
                    elapsed = time.time() - start_time
                    logger.info(
                        "   Progress: %s/%s | Elapsed: %.0fs",
                        completed,
                        len(track_ids),
                        elapsed,
                    )

        else:
            for i, track_id in enumerate(track_ids):
                tid, result, error = _execute_track(track_id)

                if error:
                    logger.error("Track %s failed: %s", track_id, error)
                elif result:
                    results[track_id] = result
                    self.notebook.add_track_result(result)

                    icon = {
                        "pass": "[OK] ",
                        "fail": "[FAIL] ",
                        "partial": "[WARN] ",
                        "stub": "[TODO] ",
                    }.get(result.status, "?")
                    name, _ = self.tracks[track_id]
                    logger.info(
                        "%s Track %s: %s - %s (%.0f/100)",
                        icon,
                        track_id,
                        name,
                        result.status.upper(),
                        result.score,
                    )

                elapsed = time.time() - start_time
                completed = i + 1
                remaining = len(track_ids) - completed
                if remaining > 0:
                    eta = (elapsed / completed) * remaining
                    logger.info(
                        "   Progress: %s/%s | Elapsed: %.0fs | ETA: %.0fs",
                        completed,
                        len(track_ids),
                        elapsed,
                        eta,
                    )

        total_time = time.time() - start_time

        output_path = self.output_dir / "verification_notebook.md"
        self.notebook.save(output_path)

        logger.info("\n" + "=" * 70)
        logger.info("[SUCCESS]  VERIFICATION COMPLETE")
        logger.info("=" * 70)
        logger.info("⏱️  Total time: %.1fs", total_time)
        logger.info("[LOG]  Output: %s", output_path)

        passed = sum(1 for r in results.values() if r.status == "pass")
        total = len(results)
        logger.info("[DATA]  Results: %s/%s tracks passed", passed, total)

        return results

    def list_tracks(self):
        """Print all available tracks."""
        logger.info("\nAvailable Verification Tracks:")
        logger.info("-" * 60)
        for tid, (name, _) in self.tracks.items():
            logger.info("  %2d. %s", tid, name)
        logger.info("-" * 60)


__all__ = ["Verifier"]
