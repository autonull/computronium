"""What the dashboard offers to start a run with, and how it starts one (TODO70).

The profiles and the axes are the surface CLI's own, read from the places the
CLI reads them, so a run started from the browser declares the same run the
command line would have declared.

Starting a run needs a campaign queue: the queue is what turns a declaration
into work. Without one the answer is the command to type — the dashboard must
never appear to have a control it does not have.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

if TYPE_CHECKING:
    from computronium.experiment.execution.campaign import CampaignSpec
    from computronium.experiment.execution.campaign_queue import CampaignQueue
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)

# The store a run lands in when the dashboard was not told one.
DEFAULT_STORE = "experiment.duckdb"


def profiles_payload() -> dict[str, Any]:
    """The run profiles as data: what the new-run form offers.

    Each profile says what it declares — its stages, its fidelity, its seeds,
    its epochs, its budget, and the axes it varies — so the reader can see
    what a profile *is* before choosing one.
    """
    from computronium.experiment.surface._cli._profiles import RUN_PROFILES

    return {
        "profiles": [
            {
                "name": profile.name,
                "description": profile.description,
                "stages": list(profile.stages),
                "fidelity": profile.fidelity,
                "task": profile.task,
                "n_seeds": profile.n_seeds,
                "epochs": profile.epochs,
                "batch_limit": profile.batch_limit,
                "budget_seconds": profile.budget_seconds,
                "param_budget": profile.param_budget,
                "objectives": list(profile.objectives),
                "policy": profile.policy,
                "axes": [
                    {
                        "axis": selection.axis.value,
                        "primitives": list(selection.selected()),
                    }
                    for selection in profile.axes
                ],
            }
            for profile in RUN_PROFILES.values()
        ]
    }


def axes_payload() -> dict[str, Any]:
    """The six structural axes and the primitives each one offers.

    A primitive that is unavailable says why: a retired row needs a recorded
    reason, not a silent omission.
    """
    return {
        "axes": [
            {
                "axis": axis.value,
                "primitives": [
                    {
                        "name": spec.name,
                        "description": spec.description,
                        "available": spec.available,
                        "unavailable_reason": spec.unavailable_reason,
                    }
                    for spec in AXES_REGISTRIES[axis].values()
                ],
            }
            for axis in StructuralAxis
        ]
    }


def build_spec(
    profile_name: str,
    overrides: dict[str, Any] | None = None,
    *,
    device: str | None = None,
) -> RunSpec:
    """The run declaration a profile and the reader's edits make.

    The same mapping the CLI uses, so a run started from the browser declares
    the run the command line would have declared.

    Args:
        profile_name: The profile the reader chose.
        overrides: The reader's edits — seeds, epochs, budget, the axes to
            vary — as the form holds them.
        device: The device to run on; the profile's own when omitted.

    Returns:
        The run declaration.

    Raises:
        ValueError: The profile is not one the surface offers.
    """
    from computronium.experiment.surface._cli._execution import (
        _apply_overrides,
        spec_from_profile,
    )
    from computronium.experiment.surface._cli._profiles import RUN_PROFILES

    if profile_name not in RUN_PROFILES:
        known = ", ".join(sorted(RUN_PROFILES))
        msg = f"unknown profile {profile_name!r}; the profiles are: {known}"
        raise ValueError(msg)
    profile = _apply_overrides(RUN_PROFILES[profile_name], overrides or {})
    return spec_from_profile(profile, device=device or "auto")


def campaign_spec(
    spec: RunSpec,
    overrides: dict[str, Any] | None = None,
    *,
    store_path: str = DEFAULT_STORE,
) -> CampaignSpec:
    """The campaign that runs a declaration.

    The edits travel as overrides, not as a spec file: the campaign runner
    derives the declaration from the profile and the overrides, and a
    declaration it derives differently from the one on screen would be a
    second truth.
    """
    from computronium.experiment.execution.campaign import CampaignRun, CampaignSpec

    return CampaignSpec(
        name=spec.profile,
        runs=[
            CampaignRun(
                name=spec.profile,
                profile=spec.profile,
                overrides=dict(overrides or {}),
                device=spec.device,
                store=store_path,
            )
        ],
        store=store_path,
    )


async def enqueue_run(
    queue: CampaignQueue | None,
    spec: RunSpec,
    overrides: dict[str, Any] | None = None,
    *,
    store_path: str = DEFAULT_STORE,
) -> dict[str, Any]:
    """Start a run, or refuse in words that name the alternative.

    The dashboard must never appear to have a control it does not have: with
    no queue attached, the honest answer is the command the reader could
    type instead.

    Args:
        queue: The campaign queue, or ``None`` when the dashboard has none.
        spec: The declaration the reader asked for.
        overrides: The reader's edits, as the campaign carries them.
        store_path: The store the run lands in.

    Returns:
        The answer: the campaign id, or the refusal with its command.
    """
    if queue is None:
        return {
            "started": False,
            "error": "no campaign queue is attached to this dashboard",
            "command": run_command(spec, store_path),
        }
    campaign = campaign_spec(spec, overrides, store_path=store_path)
    campaign_id = await queue.enqueue(campaign)
    return {
        "started": True,
        "campaign_id": campaign_id,
        "run_id": spec.profile,
        "store": store_path,
    }


def run_command(spec: RunSpec, store_path: str = DEFAULT_STORE) -> str:
    """The command that starts this run in a terminal."""
    return f"uv run comp run {spec.profile} --store {store_path}"


__all__ = [
    "DEFAULT_STORE",
    "axes_payload",
    "build_spec",
    "campaign_spec",
    "enqueue_run",
    "profiles_payload",
    "run_command",
]
