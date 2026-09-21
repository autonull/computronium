"""
Research Synthesizer.

Synthesizes high-level insights from experimental results, generating
strategic analysis, failure pattern detection, and actionable recommendations
to guide future research directions.
"""

import json
import sqlite3
import traceback

import pandas as pd

from computronium.core.logging import get_logger

__all__ = [
    "ResearchSynthesizer",
    "logger",
]
logger = get_logger()


class ResearchSynthesizer:
    """
    Synthesizes research insights from experimental results.

    Generates high-level strategic analysis and actionable recommendations.

    Attributes:
        db_path (str): Path to the results database.
    """

    def __init__(self, db_path: str) -> None:
        """
        Initialize the ResearchSynthesizer.

        Args:
            db_path (str): Path to the SQLite database.
        """
        self.db_path = db_path

    def _load_convergence_data(self, conn: sqlite3.Connection) -> pd.DataFrame:
        """
        Load detailed convergence data linked to trials.

        Args:
            conn (sqlite3.Connection): Database connection.

        Returns:
            pd.DataFrame: Convergence data.
        """
        try:
            query = """
            SELECT
                traj.trial_id,
                MAX(CASE WHEN ua.key = 'model_name'
                    THEN ua.value_json END) as model_name,
                MAX(CASE WHEN ua.key = 'task_name'
                    THEN ua.value_json END) as task_name,
                ckpt.epoch,
                ckpt.train_loss,
                ckpt.val_acc,
                ckpt.train_acc,
                ckpt.perplexity,
                ckpt.samples_seen
            FROM training_checkpoints ckpt
            JOIN training_trajectories traj ON ckpt.trajectory_id = traj.id
            JOIN trials t ON traj.trial_id = t.trial_id
            LEFT JOIN trial_user_attributes ua ON t.trial_id = ua.trial_id
            WHERE t.state = 'COMPLETE'
            GROUP BY traj.trial_id, ckpt.epoch
            ORDER BY traj.trial_id, ckpt.epoch
            """

            df = pd.read_sql(query, conn)

            # Clean up JSON strings
            for col in ["model_name", "task_name"]:
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: (
                            json.loads(x)
                            if isinstance(x, str) and x.startswith('"')
                            else x
                        )
                    )

            return df  # ruff: ignore[try-consider-else]
        except (ValueError, TypeError, OSError, KeyError, pd.errors.DatabaseError) as e:
            logger.warning("[WARN]  Error loading convergence data: %s", e)
            return pd.DataFrame()

    def synthesize_full_report(self) -> dict[str, object]:
        """
        Generate comprehensive research insights.

        Returns:
            Dict[str, object]: Structured insights dictionary.
        """
        try:  # noqa: PLR0915
            conn = sqlite3.connect(self.db_path)

            # Load Data with full metadata
            trials_df = self._get_trials_df(conn)

            # Load Convergence Data
            convergence_df = self._load_convergence_data(conn)

            try:
                failures_query = "SELECT * FROM failures"
                failures_df = pd.read_sql(failures_query, conn)
            except ValueError, TypeError, OSError, pd.errors.DatabaseError:
                logger.warning("Failed to load failures table, using empty DataFrame")
                failures_df = pd.DataFrame()

            insights = {
                "cross_algorithm_insights": self._analyze_cross_algo(trials_df),
                "task_specific_winners": self._analyze_by_task(trials_df),
                "efficiency_analysis": self._analyze_efficiency(
                    trials_df, convergence_df
                ),
                "backprop_gap_analysis": self._analyze_backprop_gap(trials_df),
                "ablation_analysis": self._analyze_ablations(trials_df),
                "statistical_significance": self._analyze_significance(trials_df),
                "failure_analysis": self._analyze_failures(failures_df),
                "quick_wins": self._find_quick_wins(trials_df, failures_df),
                "research_gaps": self._identify_gaps(trials_df),
            }
            conn.close()
            return insights  # ruff: ignore[try-consider-else]
        except Exception as e:  # broad: best-effort analysis/reporting
            traceback.print_exc()
            return {"error": str(e)}

    # Metadata rescue constants
    _KNOWN_TASKS = [
        "tiny_shakespeare",
        "char_ngram",
        "fashion_mnist",
        "mnist",
        "cifar10",
        "cartpole",
        "pendulum",
    ]

    _TIER_VALUES = ["smoke", "shallow", "standard", "deep"]

    def _get_trials_df(self, conn: sqlite3.Connection) -> pd.DataFrame:
        """
        Query and denormalize Optuna trials with full hyperparameters.

        Args:
            conn (sqlite3.Connection): Database connection.

        Returns:
            pd.DataFrame: DataFrame containing trial data.
        """
        df = self._fetch_base_trials_df(conn)
        df = self._fetch_hyperparameters(conn, df)
        df = self._deserialize_json_columns(df)
        df = df.apply(self._rescue_metadata, axis=1)  # type: ignore[return-value]
        return df  # type: ignore[return-value]
        return df

    def _fetch_base_trials_df(self, conn: sqlite3.Connection) -> pd.DataFrame:
        """Fetch base trial data from database."""
        query = """
        SELECT
            t.trial_id,
            t.state,
            s.study_name,
            v.value as accuracy,
            MAX(CASE WHEN ua.key = 'model_name' THEN ua.value_json END) as model_name,
            MAX(CASE WHEN ua.key = 'task_name' THEN ua.value_json END) as task_name,
            MAX(CASE WHEN ua.key = 'param_count' THEN ua.value_json END) as param_count,
            MAX(CASE WHEN ua.key = 'num_epochs' THEN ua.value_json END) as num_epochs,
            MAX(CASE WHEN ua.key = 'tier' THEN ua.value_json END) as tier,
            hl.param_count as param_count_actual
        FROM trials t
        LEFT JOIN studies s ON t.study_id = s.study_id
        LEFT JOIN trial_values v ON t.trial_id = v.trial_id
        LEFT JOIN trial_user_attributes ua ON t.trial_id = ua.trial_id
        LEFT JOIN hyperopt_logs hl ON t.trial_id = hl.trial_id
        WHERE t.state = 'COMPLETE'
        GROUP BY t.trial_id
        ORDER BY accuracy DESC
        """
        return pd.read_sql(query, conn)

    def _fetch_hyperparameters(self, conn: sqlite3.Connection, df: pd.DataFrame) -> pd.DataFrame:
        """Fetch and pivot hyperparameters."""
        params_query = "SELECT trial_id, param_name, param_value FROM trial_params"
        params_df = pd.read_sql(params_query, conn)
        if not params_df.empty:
            params_pivot = params_df.pivot(
                index="trial_id", columns="param_name", values="param_value"
            )
            df = df.join(params_pivot, on="trial_id")
        return df

    def _deserialize_json_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deserialize JSON columns."""
        for col in ["model_name", "task_name", "tier", "num_epochs"]:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: json.loads(x) if x and isinstance(x, str) else x
                )
        return df

    def _rescue_metadata(self, row: pd.Series) -> pd.Series:
        """Rescue missing metadata from study name and estimate missing values."""
        # Extract model_name, task_name, tier from study_name
        if not row.get("model_name") and row.get("study_name"):
            self._extract_metadata_from_study_name(row)

        # Estimate epochs if missing
        if not row.get("num_epochs") or row["num_epochs"] == 0:
            row["num_epochs"] = 10

        # Estimate param count
        row["param_count"] = self._estimate_param_count_from_row(row)

        return row

    def _extract_metadata_from_study_name(self, row: pd.Series) -> None:
        """Extract model_name, task_name, tier from study_name."""
        study_name = row["study_name"]
        for task in self._KNOWN_TASKS:
            if f"_{task}_" in study_name:
                parts = study_name.split(f"_{task}_")  # type: ignore[union-attr]
                if len(parts) >= 2:
                    row["model_name"] = parts[0]
                    row["task_name"] = task
                    tier_cand = parts[-1]
                    if tier_cand in self._TIER_VALUES:
                        row["tier"] = tier_cand
                break

    def _estimate_param_count_from_row(self, row: pd.Series) -> int:
        """Estimate parameter count from row data."""
        p_actual = row.get("param_count_actual")
        if p_actual is not None and p_actual > 0:
            return int(p_actual * 1_000_000) if p_actual < 500 else int(p_actual)

        p = row.get("param_count")
        if p is None or p == 0:
            return self._estimate_param_count(row)

        if isinstance(p, (int, float)) and p < 500:
            return int(p * 1_000_000)

        try:
            p_val = float(p)
            return int(p_val * 1_000_000) if p_val < 500 else int(p_val)
        except (ValueError, TypeError):
            return self._estimate_param_count(row)

    def _estimate_param_count(self, row: pd.Series) -> int:
        """Estimate parameter count based on hyperparameters if missing."""
        h = row.get("hidden_dim", 32)
        n_layers = row.get("num_layers", 1)
        try:
            h_int = int(h) if pd.notnull(h) else 32  # type: ignore[arg-type]
            l_int = int(n_layers) if pd.notnull(n_layers) else 1  # type: ignore[arg-type]
        except (ValueError, TypeError):
            h_int = 32
            l_int = 1

        return l_int * (h_int * h_int) + (h_int * 10)

    def _analyze_ablations(self, df: pd.DataFrame) -> list[dict[str, object]]:
        """Analyze results from ablation studies."""
        if df.empty:
            return []

        ablations = []
        try:  # noqa: PLR0915
            # Helper to check if trial is ablation
            def is_ablation(row: pd.Series) -> bool:
                if "config" in row and isinstance(row["config"], dict):
                    return bool(row["config"].get("is_ablation", False))  # type: ignore[return-value]
                return False

            ablation_trials = df[df.apply(is_ablation, axis=1)]

            for _, trial in ablation_trials.iterrows():
                config = trial["config"]  # type: ignore[assignment]
                parent_id = config.get("verified_trial_id") or config.get(  # type: ignore[union-attr]
                    "verification_of_trial_id"
                )
                param = config.get("ablation_param", "Unknown")  # type: ignore[union-attr]
                val = config.get(param, "Unknown")  # type: ignore[union-attr]

                if parent_id:
                    parent = df[df["trial_id"] == parent_id]
                    if not parent.empty:
                        parent_acc = parent.iloc[0]["accuracy"]
                        my_acc = trial["accuracy"]
                        delta = my_acc - parent_acc

                        ablations.append({
                            "model": trial.get("model_name", "Unknown"),
                            "task": trial.get("task_name", "Unknown"),
                            "ablation_param": param,
                            "ablation_value": val,
                            "accuracy": my_acc,
                            "baseline_accuracy": parent_acc,
                            "delta": delta,
                            "significant": abs(delta) > 0.02,  # 2% threshold
                        })
        except Exception as e:  # broad: best-effort analysis/reporting
            return [{"error": f"Ablation analysis error: {e}"}]

        return ablations

    def _analyze_significance(self, df: pd.DataFrame) -> list[dict[str, str | float]]:
        """Perform statistical significance tests between top models."""
        if df.empty or "model_name" not in df.columns:
            return []

        model_accs = self._collect_model_accuracies(df)
        if len(model_accs) < 2:
            return [
                {
                    "error": (
                        "Insufficient data for significance testing"
                        " (need >= 2 models with >= 3 trials)."
                    )
                }
            ]

        try:
            from scipy import stats
        except ImportError:
            return [{"error": "SciPy not installed, skipping statistical tests."}]

        return self._compute_pairwise_significance(model_accs)

    def _collect_model_accuracies(self, df: pd.DataFrame) -> dict[str, list[float]]:
        """Collect accuracy lists for each model with sufficient trials."""
        model_accs = {}
        for model in df["model_name"].dropna().unique():  # type: ignore[union-attr]
            accs = df[df["model_name"] == model]["accuracy"].dropna().tolist()  # type: ignore[union-attr]
            if len(accs) >= 3:
                model_accs[model] = accs
        return model_accs

    def _compute_pairwise_significance(self, model_accs: dict[str, list[float]]) -> list[dict[str, str | float]]:
        """Compute pairwise significance tests between models."""
        from scipy import stats

        results: list[dict[str, str | float]] = []
        models = sorted(model_accs.keys())

        for i, m1 in enumerate(models):
            for j, m2 in enumerate(models):
                if i >= j:
                    continue

                result = self._compare_models(m1, m2, model_accs, stats)
                if result:
                    results.append(result)

        results.sort(key=lambda x: x["p_value"])  # type: ignore[unknown]
        return results

    def _compare_models(
        self, m1: str, m2: str, model_accs: dict[str, list[float]], stats
    ) -> dict[str, str | float] | None:
        """Compare two models and return significance result if significant."""
        _t_stat, p_val = stats.ttest_ind(
            model_accs[m1], model_accs[m2], equal_var=False
        )

        if p_val >= 0.05:
            return None

        mean1 = sum(model_accs[m1]) / len(model_accs[m1])
        mean2 = sum(model_accs[m2]) / len(model_accs[m2])
        diff = mean1 - mean2

        winner = m1 if diff > 0 else m2
        loser = m2 if diff > 0 else m1

        return {
            "winner": winner,
            "loser": loser,
            "p_value": float(p_val),
            "mean_diff": abs(diff),
            "confidence": "High" if p_val < 0.01 else "Moderate",
        }

    def _analyze_cross_algo(self, df: pd.DataFrame) -> str | dict[str, object]:
        """Cross-algorithm performance comparison."""
        if df.empty or "model_name" not in df.columns:
            return "No model data available."

        try:  # noqa: PLR0915
            summary = (
                df
                .groupby("model_name")
                .agg({"accuracy": ["mean", "max", "std"], "trial_id": "count"})
                .round(4)
            )

            summary.columns = [
                "_".join(col).strip()
                for col in summary.columns.values  # type: ignore[unknown]
            ]
            summary = summary.rename(columns={"trial_id_count": "num_trials"})  # type: ignore[call-overload]
            summary = summary.sort_values("accuracy_max", ascending=False)

            rankings = []
            for model, row in summary.iterrows():
                rankings.append({
                    "model": model,
                    "best_accuracy": float(row["accuracy_max"]),  # type: ignore[arg-type]
                    "mean_accuracy": float(row["accuracy_mean"]),  # type: ignore[arg-type]
                    "std": float(row.get("accuracy_std", 0)),  # type: ignore[arg-type]
                    "trials": int(row["num_trials"]),  # type: ignore[arg-type]
                })

            return {"rankings": rankings, "summary_table": summary.to_dict()}
        except Exception as e:  # broad: best-effort analysis/reporting
            return f"Analysis failed: {e}"

    def _analyze_by_task(self, df: pd.DataFrame) -> dict[str, list[dict[str, object]]]:
        """Task-specific winners."""
        if df.empty or "task_name" not in df.columns:
            return {}

        task_winners = {}
        for task in df["task_name"].dropna().unique():
            task_df = (
                df[df["task_name"] == task]  # type: ignore[assignment]
                .sort_values(by="accuracy", ascending=False)  # type: ignore[call-overload]
                .head(3)
            )
            task_winners[task] = [
                {
                    "model": str(row.get("model_name", "Unknown")),  # type: ignore[arg-type]
                    "accuracy": float(row.get("accuracy", 0.0)),  # type: ignore[arg-type]
                    "params": int(row.get("param_count", 0) or 0),  # type: ignore[arg-type]
                }
                for _, row in task_df.iterrows()
            ]
        return task_winners

    def _analyze_efficiency(
        self, df: pd.DataFrame, convergence_df: pd.DataFrame
    ) -> dict[str, list[dict[str, object]]]:
        """Analyze parameter efficiency (Acc/Param) and epoch efficiency (Acc/Epoch)."""
        if df.empty:
            return {}

        analysis = {}

        # Parameter efficiency
        param_efficiency = self._compute_param_efficiency(df)
        if param_efficiency:
            analysis["top_param_efficient"] = param_efficiency

        # Epoch/sample efficiency and fastest learners (requires convergence data)
        if convergence_df is not None and not convergence_df.empty:
            epoch_analysis = self._compute_epoch_efficiency(df, convergence_df)
            analysis.update(epoch_analysis)
        elif "num_epochs" in df.columns:
            # Fallback to num_epochs if no convergence data
            epoch_efficiency = self._compute_fallback_epoch_efficiency(df)
            if epoch_efficiency:
                analysis["top_epoch_efficient"] = epoch_efficiency

        return analysis

    def _compute_param_efficiency(self, df: pd.DataFrame) -> list[dict] | None:
        """Compute top parameter-efficient models."""
        if "param_count" not in df.columns:
            return None

        df_valid = df[df["param_count"] > 0].copy()
        if df_valid.empty:
            return None

        df_valid["param_efficiency"] = df_valid["accuracy"] / (df_valid["param_count"] / 1e6)
        top_param = df_valid.nlargest(5, "param_efficiency")  # type: ignore[call-overload]
        top_param = top_param[
            ["model_name", "accuracy", "param_count", "param_efficiency"]
        ]
        return top_param.to_dict("records")  # type: ignore[return-value]

    def _compute_epoch_efficiency(
        self, df: pd.DataFrame, convergence_df: pd.DataFrame
    ) -> dict[str, list[dict]]:
        """Compute epoch and sample efficiency from convergence data."""
        analysis = {}

        trial_epochs = (
            convergence_df.groupby("trial_id")["epoch"].max().reset_index(name="actual_epochs")  # type: ignore[union-attr]
        )

        trial_samples = self._compute_trial_samples(convergence_df)

        fast_convergence = self._compute_fast_convergence(convergence_df)
        df_fast = pd.DataFrame(fast_convergence)

        df_epoch = df.merge(trial_epochs, on="trial_id", how="left")
        if not trial_samples.empty:
            df_epoch = df_epoch.merge(trial_samples, on="trial_id", how="left")
        df_epoch = df_epoch.merge(df_fast, on="trial_id", how="left")

        df_epoch["actual_epochs"] = df_epoch["actual_epochs"].fillna(
            df_epoch.get("num_epochs", 10)
        )

        df_epoch["epoch_efficiency"] = df_epoch["accuracy"] / df_epoch["actual_epochs"].replace(0, 1)

        top_epoch = df_epoch.nlargest(5, "epoch_efficiency")[
            [
                "model_name",
                "task_name",
                "accuracy",
                "actual_epochs",
                "epoch_efficiency",
            ]
        ]
        analysis["top_epoch_efficient"] = top_epoch.to_dict("records")  # type: ignore[return-value]

        if "total_samples" in df_epoch.columns:
            sample_efficiency = self._compute_sample_efficiency(df_epoch)
            if sample_efficiency:
                analysis["top_sample_efficient"] = sample_efficiency

        fastest_learners = self._compute_fastest_learners(df_epoch)
        if fastest_learners:
            analysis["fastest_learners"] = fastest_learners

        return analysis

    def _compute_trial_samples(self, convergence_df: pd.DataFrame) -> pd.DataFrame:
        """Compute total samples per trial."""
        if "samples_seen" not in convergence_df.columns:
            return pd.DataFrame(columns=["trial_id", "total_samples"])

        trial_samples = (
            convergence_df.groupby("trial_id")["samples_seen"].max().reset_index(name="total_samples")  # type: ignore[union-attr]
        )
        trial_samples = trial_samples.rename(columns={"samples_seen": "total_samples"})
        return trial_samples

    def _compute_fast_convergence(self, convergence_df: pd.DataFrame) -> list[dict]:
        """Compute epochs to reach 90% of final accuracy."""
        fast_convergence = []
        for trial_id in convergence_df["trial_id"].unique():
            t_data = convergence_df[convergence_df["trial_id"] == trial_id]
            final_acc = t_data["val_acc"].max()
            target = final_acc * 0.9
            reached = t_data[t_data["val_acc"] >= target]["epoch"].min()
            if isinstance(reached, float) and pd.isna(reached):
                reached = t_data["epoch"].max()
            fast_convergence.append({"trial_id": trial_id, "epochs_to_90": int(reached)})  # type: ignore[arg-type]
        return fast_convergence

    def _compute_sample_efficiency(self, df_epoch: pd.DataFrame) -> list[dict] | None:
        """Compute top sample-efficient models."""
        df_epoch["sample_efficiency"] = df_epoch["accuracy"] / (
            df_epoch["total_samples"] / 1e6
        ).replace(0, 0.001)
        top_sample = df_epoch.nlargest(5, "sample_efficiency")[
            [
                "model_name",
                "task_name",
                "accuracy",
                "total_samples",
                "sample_efficiency",
            ]
        ]
        return top_sample.to_dict("records")  # type: ignore[return-value]

    def _compute_fastest_learners(self, df_epoch: pd.DataFrame) -> list[dict] | None:
        """Compute fastest learners (models reaching 90% accuracy quickest)."""
        learners = df_epoch[df_epoch["accuracy"] > 0.5].copy()
        if learners.empty:
            return None

        top_fast = learners.sort_values(  # type: ignore[call-overload]
            by=["epochs_to_90", "accuracy"], ascending=[True, False]
        ).head(5)
        return top_fast[
            ["model_name", "task_name", "accuracy", "epochs_to_90"]
        ].to_dict("records")  # type: ignore[return-value]

    def _compute_fallback_epoch_efficiency(self, df: pd.DataFrame) -> list[dict] | None:
        """Fallback epoch efficiency using num_epochs column."""
        df_valid = df[df["num_epochs"] > 0].copy()
        if df_valid.empty:
            return None

        df_valid["epoch_efficiency"] = df_valid["accuracy"] / df_valid["num_epochs"]
        top_epoch = df_valid.nlargest(5, "epoch_efficiency")  # type: ignore[call-overload]
        top_epoch = top_epoch[
            [
                "model_name",
                "task_name",
                "accuracy",
                "num_epochs",
                "epoch_efficiency",
            ]
        ]
        return top_epoch.to_dict("records")  # type: ignore[return-value]

    def _analyze_failures(self, df: pd.DataFrame) -> str | dict[str, object]:
        """Failure pattern analysis."""
        if df.empty:
            return "No failures recorded."

        try:  # noqa: PLR0915
            if "failure_type" in df.columns:
                counts = df["failure_type"].value_counts().to_dict()

                patterns = []
                if any("nan" in str(k).lower() for k in counts.keys()):  # ruff: ignore[in-dict-keys]
                    patterns.append(
                        "NaN instability detected"
                        " (likely exploding gradients or high LR)"
                    )
                if any("timeout" in str(k).lower() for k in counts.keys()):  # ruff: ignore[in-dict-keys]
                    patterns.append(
                        "Timeout issues"
                        " (consider reducing model depth"
                        " or using checkpointing)"
                    )

                return {"counts": counts, "patterns": patterns}
            return "Failures exist but missing failure_type."  # ruff: ignore[try-consider-else]
        except Exception as e:  # broad: best-effort analysis/reporting
            return f"Failure analysis failed: {e}"

    def _find_quick_wins(
        self, trials: pd.DataFrame, failures: pd.DataFrame
    ) -> list[str]:
        """Actionable recommendations."""
        suggestions = []

        suggestions.extend(self._check_nan_failures(failures))
        suggestions.extend(self._check_model_failure_rates(trials, failures))
        suggestions.extend(self._check_tier_balance(trials))
        suggestions.extend(self._check_underexplored_models(trials))

        return suggestions

    def _check_nan_failures(self, failures: pd.DataFrame) -> list[str]:
        """Check for critical NaN failures."""
        if failures.empty or "failure_type" not in failures.columns:
            return []

        nan_fails = failures[
            failures["failure_type"].astype(str).str.contains("nan", case=False, na=False)
        ]
        if len(nan_fails) > 5:
            return [
                f"[CRITICAL]  {len(nan_fails)} NaN failures detected."
                f" Recommendation: Lower learning rates"
                f" globally or add gradient clipping."
            ]
        return []

    def _check_model_failure_rates(
        self, trials: pd.DataFrame, failures: pd.DataFrame
    ) -> list[str]:
        """Check for models with high failure rates."""
        if failures.empty or "model_name" not in failures.columns or trials.empty:
            return []

        fail_counts = failures["model_name"].value_counts()
        success_counts = trials["model_name"].value_counts()

        suggestions = []
        for model in fail_counts.index:
            f_count = fail_counts[model]
            s_count = success_counts.get(model, 0)
            total = f_count + s_count

            if total >= 5:
                rate = f_count / total
                if rate > 0.5:
                    suggestions.append(
                        f"[WARN]  Model '{model}' has a {rate:.0%}"
                        f" failure rate ({f_count}/{total})."
                        f" Consider debugging initialization"
                        f" or disabling."
                    )
        return suggestions

    def _check_tier_balance(self, trials: pd.DataFrame) -> list[str]:
        """Check for heavy smoke testing."""
        if trials.empty or "tier" not in trials.columns:
            return []

        tier_counts = trials["tier"].value_counts()
        smoke_count = tier_counts.get("smoke", 0)
        shallow_count = tier_counts.get("shallow", 0)
        if isinstance(smoke_count, int) and isinstance(shallow_count, int) and smoke_count > shallow_count * 2:
            return [
                "[TIP]  Heavy smoke testing detected."
                " Consider promoting successful configs"
                " to shallow/standard tiers."
            ]
        return []

    def _check_underexplored_models(self, trials: pd.DataFrame) -> list[str]:
        """Check for underexplored models."""
        if trials.empty or "model_name" not in trials.columns:
            return []

        model_counts = trials["model_name"].value_counts()
        underexplored = [str(m) for m, c in model_counts.items() if isinstance(c, int) and c < 5]
        if underexplored:
            return [
                f"[DATA]  Underexplored models:"
                f" {', '.join(underexplored[:3])}."
                f" Allocate more trials for statistical"
                f" significance."
            ]
        return []

    def _identify_gaps(self, df: pd.DataFrame) -> list[str]:
        """Identify research gaps and unexplored areas."""
        gaps = []

        if not df.empty and "task_name" in df.columns:
            explored_tasks = set(df["task_name"].dropna().unique())
            all_tasks = {
                "mnist",
                "cifar10",
                "char_ngram",
                "cartpole",
                "pendulum",
                "tiny_shakespeare",
            }
            missing = all_tasks - explored_tasks
            if missing:
                gaps.append(f"Unexplored tasks: {', '.join(missing)}")

        if not df.empty and "model_name" in df.columns:
            models = set(df["model_name"].dropna().unique())
            if "GNN" not in str(models):
                gaps.append("No Graph Neural Network experiments detected")
            if "Transformer" not in str(models):
                gaps.append("No Transformer architecture experiments detected")

        return gaps

    def _analyze_backprop_gap(self, df: pd.DataFrame) -> dict[str, object]:
        """
        Analyze performance gap between bio-plausible models and Backprop Baseline.

        This is critical for the research claim: bio-plausible algorithms should
        be competitive with or advantageous over standard backpropagation.

        Returns:
            Dict with 'gaps_by_model', 'winning_models', 'task_advantages'.
        """
        if df.empty or "model_name" not in df.columns:
            return {}

        BACKPROP_NAME = "Backprop Baseline"

        result = {
            "gaps_by_model": {},
            "winning_models": [],
            "task_advantages": {},
            "summary": {},
        }

        baseline_df = df[df["model_name"] == BACKPROP_NAME]  # type: ignore[assignment]
        if baseline_df.empty:
            result["summary"]["baseline_status"] = "No Backprop Baseline experiments found"
            return result

        baseline_by_task = self._get_baseline_by_task(baseline_df)  # type: ignore[arg-type]
        other_models = df[df["model_name"] != BACKPROP_NAME]  # type: ignore[assignment]
        if other_models.empty:
            return result

        self._compute_model_gaps(result, other_models, baseline_by_task)  # type: ignore[arg-type]
        self._compute_task_advantages(result, df, baseline_by_task, BACKPROP_NAME)
        self._finalize_results(result)

        return result

    def _get_baseline_by_task(self, baseline_df: pd.DataFrame) -> dict[str, float]:
        """Get baseline accuracy by task."""
        result = baseline_df.groupby("task_name")["accuracy"].max()
        return result.to_dict()  # type: ignore[return-value]

    def _compute_model_gaps(
        self, result: dict, other_models: pd.DataFrame, baseline_by_task: dict[str, float]
    ) -> None:
        """Compute gaps for each model vs baseline."""
        for model_name in other_models["model_name"].unique():
            model_df = other_models[other_models["model_name"] == model_name]
            model_best_by_task = model_df.groupby("task_name")["accuracy"].max().to_dict()  # type: ignore[assignment]

            gaps, wins, total_comparisons = self._compare_model_to_baseline(
                model_best_by_task, baseline_by_task
            )

            if gaps:
                self._record_model_gaps(result, model_name, gaps, wins, total_comparisons)

    def _compare_model_to_baseline(
        self, model_best_by_task: dict[str, float], baseline_by_task: dict[str, float]
    ) -> tuple[list[dict], int, int]:
        """Compare a model's best accuracies to baseline by task."""
        gaps = []
        wins = 0
        total_comparisons = 0

        for task, model_acc in model_best_by_task.items():
            if task in baseline_by_task:
                baseline_acc = baseline_by_task[task]
                gap = model_acc - baseline_acc
                total_comparisons += 1

                gaps.append({
                    "task": task,
                    "model_acc": model_acc,
                    "baseline_acc": baseline_acc,
                    "gap": gap,
                    "advantage": gap > 0,
                })

                if gap > 0:
                    wins += 1

        return gaps, wins, total_comparisons

    def _record_model_gaps(
        self, result: dict, model_name: str, gaps: list[dict], wins: int, total_comparisons: int
    ) -> None:
        """Record gap analysis for a model."""
        avg_gap = sum(g["gap"] for g in gaps) / len(gaps)
        result["gaps_by_model"][model_name] = {
            "avg_gap": float(avg_gap),
            "win_rate": float(wins / total_comparisons) if total_comparisons > 0 else 0.0,
            "comparisons": gaps,
        }

        if avg_gap > 0:
            result["winning_models"].append({
                "model": model_name,
                "avg_advantage": float(avg_gap),
                "win_rate": float(wins / total_comparisons) if total_comparisons > 0 else 0.0,
            })

    def _compute_task_advantages(
        self,
        result: dict,
        df: pd.DataFrame,
        baseline_by_task: dict[str, float],
        baseline_name: str,
    ) -> None:
        """Compute task-level advantages."""
        for task in df["task_name"].unique():
            task_df = df[df["task_name"] == task]  # type: ignore[assignment]
            baseline_acc = self._get_task_baseline_acc(task_df, baseline_name)  # type: ignore[arg-type]
            if baseline_acc <= 0:
                continue

            other_best = self._get_other_models_best_acc(task_df, baseline_name)  # type: ignore[arg-type]
            if other_best.empty:
                continue

            best_other = other_best.max()
            best_other_model = other_best.idxmax()
            gap = best_other - baseline_acc

            result["task_advantages"][task] = {
                "baseline_acc": float(baseline_acc),
                "best_bio_model": str(best_other_model),
                "best_bio_acc": float(best_other),
                "advantage": float(gap),
                "bio_wins": bool(gap > 0),
            }

    def _get_task_baseline_acc(self, task_df: pd.DataFrame, baseline_name: str) -> float:
        """Get baseline accuracy for a task."""
        vals = task_df[task_df["model_name"] == baseline_name]["accuracy"]
        max_val = vals.max()
        return float(max_val.item()) if pd.notna(max_val) else 0.0  # type: ignore[return-value]

    def _get_other_models_best_acc(
        self, task_df: pd.DataFrame, baseline_name: str
    ) -> pd.Series:
        """Get best accuracy for non-baseline models by task."""
        return (
            task_df[task_df["model_name"] != baseline_name]
            .groupby("model_name")["accuracy"]
            .max()
        )  # type: ignore[return-value]

    def _finalize_results(self, result: dict) -> None:
        """Finalize results with sorting and summary."""
        if result["winning_models"]:
            result["winning_models"].sort(key=lambda x: x["avg_advantage"], reverse=True)

        total_bio_wins = sum(
            1 for t in result["task_advantages"].values() if t["bio_wins"]
        )
        total_tasks = len(result["task_advantages"])
        result["summary"] = {
            "total_tasks": total_tasks,
            "bio_wins_on_tasks": total_bio_wins,
            "win_rate": total_bio_wins / total_tasks if total_tasks > 0 else 0,
            "models_beating_baseline": len(result["winning_models"]),
        }
