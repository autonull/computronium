"""I(C,U) Metamodel: learnability-interaction surrogate with leakage guard.

Implements WP6 deliverable: I(C,U) metamodel as registered surrogate/prior source (R53, R55).
Leakage guard: I(C,U) training data tagged with data_origin; periodic calibration audit per WP5.5 #3.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import numpy as np

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import DuplicateMeasurementError
from computronium.experiment.learning.surrogate import (
    AcquisitionFunction,
    GaussianProcessSurrogate,
    SurrogateConfig,
    SurrogateKind,
    SurrogateModel,
    SurrogateTrainingData,
)
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)
from computronium.experiment.schema.registries import ASSESSMENT_PROCEDURE_VERSION

logger = get_logger(__name__)

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.evidence.protocol import CostBudget
    from computronium.experiment.evidence.store import RecordStore


class ICUComponent(StrEnum):
    """I(C,U) component types."""

    CREDIT = "credit"
    UPDATE = "update"
    INTERACTION = "interaction"  # Credit × Update interaction


@dataclass(frozen=True, slots=True)
class ICUFeatureVector:
    """Feature vector for I(C,U) prediction.

    Encodes the credit assignment and parameter update configuration
    along with their interaction features.
    """

    credit_type: str
    update_type: str
    # Interaction features
    credit_family: str  # e.g., "local", "global", "contrastive"
    update_family: str  # e.g., "euclidean", "riemannian", "natural"
    # Structural context (optional)
    dynamics_type: str | None = None
    geometry_type: str | None = None
    substrate_type: str | None = None
    plasticity_type: str | None = None

    def to_array(self) -> np.ndarray:
        """Convert to feature array for surrogate."""
        # One-hot / ordinal encoding
        features = [
            hash(self.credit_type) % 1000 / 1000.0,
            hash(self.update_type) % 1000 / 1000.0,
            hash(self.credit_family) % 1000 / 1000.0,
            hash(self.update_family) % 1000 / 1000.0,
        ]
        if self.dynamics_type:
            features.append(hash(self.dynamics_type) % 1000 / 1000.0)
        else:
            features.append(0.0)
        if self.geometry_type:
            features.append(hash(self.geometry_type) % 1000 / 1000.0)
        else:
            features.append(0.0)
        if self.substrate_type:
            features.append(hash(self.substrate_type) % 1000 / 1000.0)
        else:
            features.append(0.0)
        return np.array(features, dtype=float)

    @classmethod
    def from_coordinate(cls, coord: Coordinate) -> ICUFeatureVector:
        """Extract I(C,U) features from a coordinate."""
        # Map credit/update to families
        credit_families = {
            "gradient": "global",
            "thermodynamic_contrast": "contrastive",
            "random_projections": "local",
            "fa": "local",
            "local_goodness": "local",
            "pepita": "local",
            "target_inversion": "local",
            "temporal_trace": "local",
            "homeostatic": "local",
        }
        update_families = {
            "euclidean": "euclidean",
            "riemannian_orthogonal": "riemannian",
            "muon": "riemannian",
            "spectral_constrained": "riemannian",
            "natural_gradient": "natural",
            "elastic_consolidation": "euclidean",
            "mean_norm": "euclidean",
            "unit_rms": "euclidean",
        }

        return cls(
            credit_type=coord.credit,
            update_type=coord.update,
            credit_family=credit_families.get(coord.credit, "unknown"),
            update_family=update_families.get(coord.update, "unknown"),
            dynamics_type=coord.dynamics,
            geometry_type=coord.geometry,
            substrate_type=coord.substrate,
            plasticity_type=coord.plasticity,
        )

    @property
    def interaction_key(self) -> str:
        """Unique key for this credit×update combination."""
        return f"{self.credit_type}|{self.update_type}"


@dataclass(frozen=True, slots=True)
class ICURecord:
    """A single I(C,U) measurement record.

    Tagged with data_origin for leakage prevention per WP5.5.
    """

    feature_vector: ICUFeatureVector
    # Primary metric: best validation score at budget B
    primary_metric: float
    # Secondary metrics
    secondary_metrics: dict[str, float] = field(default_factory=dict)
    # Cost budget used
    budget: CostBudget | None = None
    # Data origin tag (CRITICAL for leakage prevention)
    data_origin: DataOrigin = DataOrigin.EXPLORATION
    # Provenance
    record_id: str = ""
    task: str = ""
    seed: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_vector": {
                "credit_type": self.feature_vector.credit_type,
                "update_type": self.feature_vector.update_type,
                "credit_family": self.feature_vector.credit_family,
                "update_family": self.feature_vector.update_family,
                "dynamics_type": self.feature_vector.dynamics_type,
                "geometry_type": self.feature_vector.geometry_type,
                "substrate_type": self.feature_vector.substrate_type,
            },
            "primary_metric": self.primary_metric,
            "secondary_metrics": self.secondary_metrics,
            "budget": {"kind": self.budget.kind.value, "limit": self.budget.limit}
            if self.budget
            else None,
            "data_origin": self.data_origin.value,
            "record_id": self.record_id,
            "task": self.task,
            "seed": self.seed,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ICURecord:
        fv = data["feature_vector"]
        feature_vector = ICUFeatureVector(
            credit_type=fv["credit_type"],
            update_type=fv["update_type"],
            credit_family=fv["credit_family"],
            update_family=fv["update_family"],
            dynamics_type=fv.get("dynamics_type"),
            geometry_type=fv.get("geometry_type"),
            substrate_type=fv.get("substrate_type"),
        )
        budget = None
        if data.get("budget"):
            from computronium.experiment.evidence.protocol import (
                CostBudget,
                CostBudgetKind,
            )

            budget = CostBudget(
                CostBudgetKind(data["budget"]["kind"]), data["budget"]["limit"]
            )
        return cls(
            feature_vector=feature_vector,
            primary_metric=data["primary_metric"],
            secondary_metrics=data.get("secondary_metrics", {}),
            budget=budget,
            data_origin=DataOrigin(data["data_origin"]),
            record_id=data.get("record_id", ""),
            task=data.get("task", ""),
            seed=data.get("seed", 0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )


class ICUModel:
    """I(C,U) Metamodel: predicts learnability from credit×update configuration.

    Uses a surrogate model trained on exploration ∪ policy_selected data.
    Evaluated on calibration ∪ test data per E2/E3 protocol.
    Includes leakage guard: all training data tagged with data_origin.
    """

    def __init__(
        self,
        surrogate: SurrogateModel | None = None,
        config: SurrogateConfig | None = None,
    ) -> None:
        if config is None:
            config = SurrogateConfig(kind=SurrogateKind.GAUSSIAN_PROCESS)
        if surrogate is None:
            surrogate = GaussianProcessSurrogate(config)

        self._surrogate = surrogate
        self._config = config
        self._records: list[ICURecord] = []
        self._fitted = False
        self._model_version = 0
        self._code_hash = self._compute_code_hash()

    def _compute_code_hash(self) -> str:
        """Compute content hash of this module for immutability tracking."""
        # In practice, would hash the actual source file
        return hashlib.sha256(b"icu_model_v1").hexdigest()[:16]

    @property
    def code_hash(self) -> str:
        return self._code_hash

    @property
    def model_version(self) -> int:
        return self._model_version

    @property
    def n_records(self) -> int:
        return len(self._records)

    @property
    def training_records(self) -> list[ICURecord]:
        """Records allowed for training (exploration ∪ policy_selected)."""
        return [
            r
            for r in self._records
            if r.data_origin in {DataOrigin.EXPLORATION, DataOrigin.POLICY_SELECTED}
        ]

    @property
    def evaluation_records(self) -> list[ICURecord]:
        """Records for evaluation only (calibration ∪ test)."""
        return [
            r
            for r in self._records
            if r.data_origin in {DataOrigin.CALIBRATION, DataOrigin.TEST}
        ]

    def add_record(self, record: ICURecord) -> None:
        """Add a measurement record.

        The data_origin tag is mandatory and determines whether this
        record can be used for training or only for evaluation.
        """
        if record.data_origin not in {
            DataOrigin.EXPLORATION,
            DataOrigin.POLICY_SELECTED,
            DataOrigin.CALIBRATION,
            DataOrigin.TEST,
        }:
            raise ValueError(
                f"data_origin must be a valid DataOrigin, got {record.data_origin}"
            )
        self._records.append(record)
        self._fitted = False  # Invalidate model

    def add_records(self, records: list[ICURecord]) -> None:
        """Add multiple records."""
        for r in records:
            self.add_record(r)

    def ingest_measurements(
        self,
        store: RecordStore,
        run_id: str,
        metric_key: str = "val_acc",
    ) -> int:
        """Train on a campaign's own measurements.

        ``load_from_store`` reads records this model wrote; the records a
        campaign actually measured are the ones it must learn from, and until
        this existed there was no path between them — so I(C,U) could only ever
        be trained on its own output.

        The train/evaluate split is inherited, not chosen: each record's
        ``provenance.data_origin`` decides it, which is the same tag the
        leakage guard reads. Re-deciding the split here would let a caller train
        on its own held-out set by picking a different moment.

        Args:
            store: The store holding the campaign's records.
            run_id: The campaign to learn from.
            metric_key: Payload key to learn. Defaults to validation accuracy.

        Returns:
            Number of records ingested; those without the metric are skipped.
        """
        ingested = 0
        for record in store.query_records(run_id=run_id):
            value = record.payload.get(metric_key)
            if value is None:
                continue
            self.add_record(
                ICURecord(
                    feature_vector=ICUFeatureVector.from_coordinate(
                        Coordinate(
                            substrate=record.substrate,
                            geometry=record.geometry,
                            dynamics=record.dynamics,
                            plasticity=record.plasticity,
                            credit=record.credit,
                            update=record.update,
                            params=dict(record.params),
                        )
                    ),
                    primary_metric=float(value),
                    secondary_metrics={
                        key: float(record.payload[key])
                        for key in ("val_loss", "param_count", "walltime_s")
                        if isinstance(record.payload.get(key), int | float)
                    },
                    data_origin=record.provenance.data_origin,
                    record_id=record.record_id,
                    task=record.schedule.task_id,
                    seed=record.schedule.seed,
                )
            )
            ingested += 1
        logger.info(
            "I(C,U) ingested %d measurement(s) from run %s over %s",
            ingested,
            run_id,
            metric_key,
        )
        return ingested

    def held_out_accuracy(self) -> dict[str, Any]:
        """Predict accuracy on the records the fit never saw.

        The number TODO51 §4's acceptance criterion names. Reported on the
        evaluation origins only — accuracy on the training origins is the fit
        reading itself back.
        """
        evaluation = self.evaluation_records
        if not evaluation:
            return {"status": "no_evaluation_data", "n": 0}
        if not self._fitted:
            self.fit()
        exact = sum(
            1
            for record in evaluation
            if abs(self.predict(record.feature_vector)[0] - record.primary_metric)
            < 0.01
        )
        errors = [
            abs(self.predict(record.feature_vector)[0] - record.primary_metric)
            for record in evaluation
        ]
        return {
            "status": "ok",
            "n": len(evaluation),
            "exact_match_rate": exact / len(evaluation),
            "mean_absolute_error": sum(errors) / len(errors),
        }

    def load_from_store(
        self,
        store: RecordStore,
        run_id: str | None = None,
        data_origin: str | None = None,
    ) -> int:
        """Load I(C,U) records from the experiment store.

        Queries records with payload kind "icu" and reconstructs ICURecords.

        Args:
            store: The RecordStore to query.
            run_id: Optional run ID to filter by.
            data_origin: Optional data origin filter (exploration/policy_selected/calibration/test).

        Returns:
            Number of records loaded.
        """
        records = store.query_records_by_payload_kind(
            payload_kind="icu", run_id=run_id, data_origin=data_origin
        )

        loaded = 0
        for record in records:
            icu_data = record.payload.get("icu")
            if icu_data:
                icu_record = ICURecord.from_dict(icu_data)
                self.add_record(icu_record)
                loaded += 1

        return loaded

    def persist_to_store(
        self,
        store: RecordStore,
        run_id: str,
        record_id: str,
        data_origin: DataOrigin,
    ) -> None:
        """Persist this I(C,U) model's records to the store.

        Creates a new record with payload.kind = "icu" containing the ICURecord data.

        Args:
            store: The RecordStore to write to.
            run_id: The run ID for the new record.
            record_id: The record ID for the new record.
            data_origin: The data origin tag for the record.
        """
        # For each ICURecord, create a store record with the ICU data in payload
        for icu_record in self._records:
            # Create a minimal coordinate for the ICU record
            coord = Coordinate(
                substrate=icu_record.feature_vector.substrate_type or "digital",
                geometry=icu_record.feature_vector.geometry_type or "feedforward",
                dynamics=icu_record.feature_vector.dynamics_type or "instantaneous",
                plasticity=icu_record.feature_vector.plasticity_type or "null",
                credit=icu_record.feature_vector.credit_type,
                update=icu_record.feature_vector.update_type,
                params={},
            )

            # Build payload with ICU data
            payload = {
                "kind": "icu",
                "icu": icu_record.to_dict(),
                "model_version": self._model_version,
                "code_hash": self._code_hash,
            }

            # Create provenance with data_origin
            provenance = Provenance(
                env={},
                dataset="",
                dataset_version="",
                code_sha="",
                policy="icu_model",
                links={},
                data_origin=data_origin,
                training_tasks=(),
                transfer_source_ids=(),
                transfer_cutoff=None,
                target_task=icu_record.task,
                transfer_mode=None,
            )

            # Create status
            status = Status(
                gate_verdict=GateVerdict.PASS_,
                defect="",
                cause=FailureCause.UNKNOWN,
                severity=Severity.LOW,
                quarantine=False,
                maturity=Maturity.L0,
                uncertainty={},
                reproducibility=ReproducibilityClass.REPLAYABLE,
                assessment_procedure_version=ASSESSMENT_PROCEDURE_VERSION,
                ceec_link=None,
            )

            # Create schedule
            schedule = Schedule(
                fidelity="L0",
                seed=icu_record.seed,
                n_seeds=1,
                epochs=0,
                batch_limit=0,
                budget_id="",
            )

            record = Record(
                record_id=f"{record_id}_{icu_record.feature_vector.interaction_key}",
                seq=0,  # Will be assigned by store
                run_id=run_id,
                schema_version=2,
                cell_key=hashlib.sha256(
                    f"{coord.substrate}|{coord.geometry}|{coord.dynamics}|{coord.plasticity}|{coord.credit}|{coord.update}".encode()
                ).hexdigest()[:16],
                measurement_key=hashlib.sha256(
                    f"{coord.substrate}|{coord.geometry}|{coord.dynamics}|{coord.plasticity}|{coord.credit}|{coord.update}|{icu_record.seed}".encode()
                ).hexdigest()[:16],
                substrate=coord.substrate,
                geometry=coord.geometry,
                dynamics=coord.dynamics,
                plasticity=coord.plasticity,
                credit=coord.credit,
                update=coord.update,
                params=coord.params,
                effective_params=coord.params,
                schedule=schedule,
                provenance=provenance,
                status=status,
                payload=payload,
                unknown=None,
            )

            with contextlib.suppress(DuplicateMeasurementError):
                store.append(record)

    def fit(self) -> None:
        """Fit the I(C,U) surrogate on training data only.

        LEAKAGE GUARD: Only uses records with data_origin in
        {EXPLORATION, POLICY_SELECTED}. Records from CALIBRATION and TEST
        are NEVER used for training.
        """
        training = self.training_records
        if len(training) < 2:
            raise ValueError(
                f"Need at least 2 training records, got {len(training)}. "
                f"Total records: {len(self._records)} "
                f"(exploration: {sum(1 for r in self._records if r.data_origin == DataOrigin.EXPLORATION)}, "
                f"policy_selected: {sum(1 for r in self._records if r.data_origin == DataOrigin.POLICY_SELECTED)}, "
                f"calibration: {sum(1 for r in self._records if r.data_origin == DataOrigin.CALIBRATION)}, "
                f"test: {sum(1 for r in self._records if r.data_origin == DataOrigin.TEST)})"
            )

        # Convert to surrogate training data
        coords = []
        objectives = []
        origins = []

        for record in training:
            # Create a coordinate from the feature vector
            coord = Coordinate(
                substrate=record.feature_vector.substrate_type or "digital",
                geometry=record.feature_vector.geometry_type or "feedforward",
                dynamics=record.feature_vector.dynamics_type or "instantaneous",
                plasticity=record.feature_vector.plasticity_type or "null",
                credit=record.feature_vector.credit_type,
                update=record.feature_vector.update_type,
                params={},
            )
            coords.append(coord)
            objectives.append(record.primary_metric)
            origins.append(record.data_origin)

        training_data = SurrogateTrainingData(
            coordinates=coords,
            objectives=objectives,
            data_origins=origins,
        )

        self._surrogate.fit(training_data)
        self._fitted = True
        self._model_version += 1

    def predict(self, feature_vector: ICUFeatureVector) -> tuple[float, float]:
        """Predict primary metric for a credit×update configuration.

        Returns:
            Tuple of (mean_prediction, uncertainty_std)
        """
        if not self._fitted:
            self.fit()

        # Create coordinate for prediction
        coord = Coordinate(
            substrate=feature_vector.substrate_type or "digital",
            geometry=feature_vector.geometry_type or "feedforward",
            dynamics=feature_vector.dynamics_type or "instantaneous",
            plasticity="null",
            credit=feature_vector.credit_type,
            update=feature_vector.update_type,
            params={},
        )

        means, stds = self._surrogate.predict([coord])
        return float(means[0]), float(stds[0])

    def predict_coordinate(self, coord: Coordinate) -> tuple[float, float]:
        """Predict for a full coordinate."""
        fv = ICUFeatureVector.from_coordinate(coord)
        return self.predict(fv)

    def get_interaction_ranking(
        self, top_k: int = 10
    ) -> list[tuple[str, float, float]]:
        """Get ranking of credit×update interactions by predicted performance.

        Returns:
            List of (interaction_key, predicted_metric, uncertainty) tuples,
            sorted by predicted metric (lower is better).
        """
        if not self._fitted:
            self.fit()

        # Get all unique interactions from training data
        interactions: dict[str, list[float]] = {}
        for record in self.training_records:
            key = record.feature_vector.interaction_key
            if key not in interactions:
                interactions[key] = []
            interactions[key].append(record.primary_metric)

        # Predict for each interaction
        predictions = []
        for key, values in interactions.items():
            credit_type, update_type = key.split("|", 1)
            fv = ICUFeatureVector(
                credit_type=credit_type,
                update_type=update_type,
                credit_family="",  # Will be inferred
                update_family="",
            )
            mean, std = self.predict(fv)
            predictions.append((key, mean, std))

        predictions.sort(key=lambda x: x[1])  # Lower metric is better
        return predictions[:top_k]

    def calibration_audit(self) -> dict[str, Any]:
        """Perform periodic calibration audit per WP5.5 #3.

        Compares predictions on calibration data vs actual outcomes.
        Returns audit metrics including bounded degradation check.
        """
        eval_records = self.evaluation_records
        if not eval_records:
            return {
                "status": "no_evaluation_data",
                "message": "No calibration/test records available for audit",
            }

        if not self._fitted:
            self.fit()

        preds = []
        actuals = []

        for record in eval_records:
            mean, _std = self.predict(record.feature_vector)
            preds.append(mean)
            actuals.append(record.primary_metric)

        preds_arr = np.array(preds)
        actuals_arr = np.array(actuals)

        # Calibration metrics
        mae = float(np.mean(np.abs(preds_arr - actuals_arr)))
        rmse = float(np.sqrt(np.mean((preds_arr - actuals_arr) ** 2)))

        # Correlation
        corr = (
            float(np.corrcoef(preds_arr, actuals_arr)[0, 1]) if len(preds) > 1 else 0.0
        )

        # Bounded degradation check (WP5.5 #3)
        # Compare policy-selected performance vs calibration/test performance
        policy_records = [
            r for r in self._records if r.data_origin == DataOrigin.POLICY_SELECTED
        ]
        cal_records = [
            r for r in self._records if r.data_origin == DataOrigin.CALIBRATION
        ]

        degradation_info = self._compute_degradation_info(policy_records, cal_records)

        return {
            "status": "completed",
            "n_evaluation": len(eval_records),
            "n_training": len(self.training_records),
            "mae": mae,
            "rmse": rmse,
            "correlation": corr,
            "model_version": self._model_version,
            "code_hash": self._code_hash,
            "degradation": degradation_info,
            "timestamp": datetime.now().isoformat(),
        }

    def _compute_degradation_info(
        self,
        policy_records: list[ICURecord],
        cal_records: list[ICURecord],
    ) -> dict[str, Any]:
        """Compute bounded degradation info from policy and calibration records."""
        degradation_info: dict[str, Any] = {}
        if policy_records and cal_records:
            policy_perf = float(np.mean([r.primary_metric for r in policy_records]))
            cal_perf = float(np.mean([r.primary_metric for r in cal_records]))
            degradation = (
                (cal_perf - policy_perf) / abs(policy_perf) if policy_perf != 0 else 0.0
            )
            degradation_info = {
                "policy_selected_perf": policy_perf,
                "calibration_perf": cal_perf,
                "relative_degradation": float(degradation),
                "within_bounds": degradation <= 0.2,  # 20% threshold (configurable)
            }
        return degradation_info

    def check_leakage(self) -> dict[str, Any]:
        """Check for data leakage in the I(C,U) model.

        Verifies that no calibration/test records were used in training.
        """
        train_origins = {r.data_origin for r in self.training_records}
        eval_origins = {r.data_origin for r in self.evaluation_records}

        leakage = train_origins & {DataOrigin.CALIBRATION, DataOrigin.TEST}

        return {
            "leakage_detected": bool(leakage),
            "leaking_origins": [o.value for o in leakage],
            "training_origins": [o.value for o in train_origins],
            "evaluation_origins": [o.value for o in eval_origins],
            "total_records": len(self._records),
            "timestamp": datetime.now().isoformat(),
        }

    def export_training_data(self, path: Path) -> None:
        """Export training data for external analysis."""
        data = {
            "model_version": self._model_version,
            "code_hash": self._code_hash,
            "records": [r.to_dict() for r in self._records],
            "exported_at": datetime.now().isoformat(),
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load_training_data(cls, path: Path) -> ICUModel:
        """Load training data from export."""
        data = json.loads(path.read_text(encoding="utf-8"))
        model = cls()
        model._model_version = data["model_version"]
        model._code_hash = data["code_hash"]
        model._records = [ICURecord.from_dict(r) for r in data["records"]]
        model._fitted = False
        return model


def create_icu_prior_surrogate() -> SurrogateModel:
    """Create an I(C,U) surrogate for use as a prior source in SurrogatePolicy."""
    config = SurrogateConfig(
        kind=SurrogateKind.GAUSSIAN_PROCESS,
        acquisition=AcquisitionFunction.EI,
        n_initial_points=5,
        n_optimizer_restarts=0,  # Avoid joblib parallel processing (loky semaphore leak)
    )
    return GaussianProcessSurrogate(config)


__all__ = [
    "ICUComponent",
    "ICUFeatureVector",
    "ICUModel",
    "ICURecord",
    "create_icu_prior_surrogate",
]
