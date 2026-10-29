"""Pydantic models applied at the store's I/O boundary."""

from __future__ import annotations

from typing import Any

# =========================================================================
# Pydantic v2 Models for I/O Validation
# =========================================================================

try:  # ruff: ignore[too-many-statements-in-try-clause]
    from typing import Annotated

    from pydantic import BaseModel, ConfigDict, Field

    class ScheduleModel(BaseModel):
        """Pydantic model for Schedule validation at I/O boundaries."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        fidelity: Annotated[str, Field(pattern="^(L0|L1|L2)$")]
        seed: Annotated[int, Field(ge=0)]
        n_seeds: Annotated[int, Field(gt=0)]
        epochs: Annotated[int, Field(gt=0)]
        batch_limit: Annotated[int, Field(ge=0)]
        budget_id: str
        task_id: str = ""
        param_budget: Annotated[int, Field(ge=0)] = 0
        device: Annotated[str, Field(pattern="^(cpu|cuda|auto)$")] = "auto"
        precision: Annotated[str, Field(pattern="^(fp32|fp16|bf16)$")] = "fp32"

    class ProvenanceModel(BaseModel):
        """Pydantic model for Provenance validation at I/O boundaries."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        env: dict[str, str]
        dataset: str
        dataset_version: str
        code_sha: str
        policy: str
        links: dict[str, str]
        data_origin: str = "exploration"
        training_tasks: list[str] = []
        transfer_source_ids: list[str] = []
        transfer_cutoff: str | None = None
        target_task: str | None = None
        transfer_mode: str | None = None

    class StatusModel(BaseModel):
        """Pydantic model for Status validation at I/O boundaries."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        gate_verdict: Annotated[str, Field(pattern="^(PASS|FAIL|QUARANTINE|PENDING)$")]
        defect: str
        cause: Annotated[
            str,
            Field(
                pattern="^(unknown|numerical|timeout|oom|invalid_config|runtime_error|constraint_violation|divergence)$"
            ),
        ]
        severity: Annotated[str, Field(pattern="^(low|medium|high|critical)$")]
        quarantine: bool
        maturity: Annotated[str, Field(pattern="^(l0|l1|l2)$")]
        uncertainty: dict[str, Any]
        reproducibility: Annotated[
            str,
            Field(
                pattern="^(replayable|computationally_reproducible|scientifically_reproducible)$"
            ),
        ]
        assessment_procedure_version: str
        ceec_link: str | None = None

    class RecordInputModel(BaseModel):
        """Pydantic model for Record input validation (create/append)."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        run_id: str
        coordinate: dict[str, Any]
        schedule: ScheduleModel
        provenance: ProvenanceModel
        status: StatusModel
        payload: dict[str, Any]
        unknown: dict[str, Any] | None = None
        schema_version: int = 2

    class RecordOutputModel(BaseModel):
        """Pydantic model for Record output validation (query results)."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        record_id: str
        seq: int
        run_id: str
        schema_version: int
        cell_key: str
        measurement_key: str
        substrate: str
        geometry: str
        dynamics: str
        plasticity: str
        credit: str
        update: str
        params: dict[str, Any]
        schedule: ScheduleModel
        provenance: ProvenanceModel
        status: StatusModel
        payload: dict[str, Any]
        unknown: dict[str, Any] | None = None

    # Validation helpers
    def validate_record_input(data: dict[str, Any]) -> RecordInputModel:
        """Validate record input data using Pydantic."""
        return RecordInputModel.model_validate(data)

    def validate_record_output(data: dict[str, Any]) -> RecordOutputModel:
        """Validate record output data using Pydantic."""
        return RecordOutputModel.model_validate(data)

except ImportError:
    # Pydantic not available - provide no-op validators
    class _MissingPydantic:
        def __getattr__(self, name: str) -> Any:
            raise ImportError(
                "pydantic v2 required for I/O validation. Install with: uv add pydantic"
            )

    validate_record_input = _MissingPydantic()  # type: ignore[assignment]
    validate_record_output = _MissingPydantic()  # type: ignore[assignment]
    ScheduleModel = _MissingPydantic  # type: ignore[assignment]
    ProvenanceModel = _MissingPydantic  # type: ignore[assignment]
    StatusModel = _MissingPydantic  # type: ignore[assignment]
    RecordInputModel = _MissingPydantic  # type: ignore[assignment]
    RecordOutputModel = _MissingPydantic  # type: ignore[assignment]
