"""Mutation Explorer (M2.14 → M3) — valid Tier 1/2 proposals with Constitution pre-check."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class MutationProposal:
    """One valid mutation proposal with Constitution pre-check."""

    proposal_id: str
    mutation_type: str  # "DuplicateAndPerturb", "SpliceOperator", "CoordinateSwap"
    tier: int  # 1 = structural, 2 = algorithmic
    description: str
    constitution_checks: dict[str, bool]  # invariant -> passed
    estimated_slope: float
    estimated_resource_delta: float
    metadata: dict[str, Any] = None  # type: ignore[assignment]


class MutationExplorer(BasePanel):
    """Mutation Explorer: from current Ω, show valid Tier 1/2 proposals.

    Each proposal includes Constitution pre-check via SystemConfig.validate()
    and StabilityMonitor fast-proxy.
    """

    def __init__(
        self,
        proposals: list[MutationProposal] | None = None,
        current_genome_size: int = 0,
    ) -> None:
        super().__init__(
            panel_key="mutation_explorer",
            plain_explanation=(
                "This panel shows what the system could try next. Each "
                "proposal is a recipe change that passes basic validity checks "
                "and the Constitution stability guard."
            ),
            why_explanation=(
                "Before running a mutation, the system checks: (1) Is it a "
                "valid Registry primitive combination? (2) Does it pass the "
                "Constitution stability guard? (3) Will it fit in the resource "
                "budget? Only viable proposals are shown."
            ),
            expert_explanation=(
                "Per AUTOTILE.md §2.3: Tier 1 (structural) and Tier 2 "
                "(algorithmic) mutations from current Ω. Valid proposals: "
                "DuplicateAndPerturb (new nodes/edges), SpliceOperator (swap "
                "Registry primitive), CoordinateSwap (axis change). Each "
                "pre-checked via SystemConfig.validate() and StabilityMonitor "
                "fast-proxy (ρ(J_F) ≤ τ, passivity, resource ceiling). "
                "Tier 3 (meta) excluded per AUTOTILE.md §7.7."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/auto-evolve/mutations.html",
        )
        self.proposals = proposals or []
        self.current_genome_size = current_genome_size

    def set_proposals(self, proposals: list[MutationProposal]) -> None:
        """Set mutation proposals."""
        self.proposals = proposals
        self._refresh()

    def set_current_genome_size(self, size: int) -> None:
        """Set current genome size."""
        self.current_genome_size = size
        self._refresh()

    def render(self) -> ui.element:
        """Render the mutation explorer."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("mutation_explorer")

            # Current genome status
            with ui.row().classes("w-full items-center gap-4 mb-4"):
                ui.icon(ICONS["genome"]).classes("text-2xl text-primary")
                ui.label(
                    f"Current Genome Size: |Ω| = {self.current_genome_size}"
                ).classes("text-h6")

            if not self.proposals:
                ui.label(
                    "No valid mutation proposals — run Constitution check first."
                ).classes("text-grey")
                return panel

            # Summary
            tier1 = [p for p in self.proposals if p.tier == 1]
            tier2 = [p for p in self.proposals if p.tier == 2]
            all_pass = sum(
                1 for p in self.proposals if all(p.constitution_checks.values())
            )

            with ui.row().classes("w-full gap-4 mb-4"):
                self._stat_card("Tier 1 (Structural)", len(tier1), ICONS["mutation"])
                self._stat_card(
                    "Tier 2 (Algorithmic)", len(tier2), ICONS["constitution"]
                )
                self._stat_card("All Checks Pass", all_pass, ICONS["success"])
                self._stat_card("Total Proposals", len(self.proposals), ICONS["probe"])

            # Proposals grouped by tier
            for tier_label, tier_proposals in [
                ("Tier 1: Structural", tier1),
                ("Tier 2: Algorithmic", tier2),
            ]:
                if not tier_proposals:
                    continue

                ui.label(tier_label).classes("text-h6 mt-4 mb-2")

                for proposal in tier_proposals:
                    self._render_proposal(proposal)

        return panel

    def _render_proposal(self, proposal: MutationProposal) -> None:
        """Render one mutation proposal."""
        all_passed = all(proposal.constitution_checks.values())
        border_color = "positive" if all_passed else "warning"

        with (
            ui
            .card()
            .classes("w-full")
            .props(
                f"flat bordered style=border-left: 4px solid var(--color-{border_color})"
            ),
            ui.row().classes("w-full items-start gap-4"),
        ):
            self._render_proposal_header(proposal, all_passed)
            self._render_proposal_body(proposal, all_passed)

    def _render_proposal_header(
        self, proposal: MutationProposal, all_passed: bool
    ) -> None:
        """Render proposal header with icon and badges."""
        tier_icon = ICONS["mutation"] if proposal.tier == 1 else ICONS["constitution"]
        ui.icon(tier_icon).classes("text-2xl text-primary shrink-0")

        with ui.column().classes("flex-1 gap-2"):
            with ui.row().classes("w-full items-center gap-2 flex-wrap"):
                ui.label(proposal.mutation_type).classes("text-bold")
                ui.badge(
                    f"Tier {proposal.tier}",
                    color="primary" if proposal.tier == 1 else "secondary",
                ).props("outline")
                ui.badge(
                    "✓ All Pass" if all_passed else "⚠ Some Fail",
                    color="positive" if all_passed else "warning",
                ).props("outline")

            ui.label(proposal.description).classes("text-body text-grey")

    def _render_proposal_body(
        self, proposal: MutationProposal, all_passed: bool
    ) -> None:
        """Render proposal constitution checks and estimates."""
        # Constitution checks
        ui.label("Constitution Pre-Check:").classes("text-bold text-sm mt-2")
        with ui.row().classes("w-full gap-2 flex-wrap"):
            for check_name, passed in proposal.constitution_checks.items():
                self._render_check_item(check_name, passed)

        # Estimates
        with ui.row().classes("w-full gap-4 mt-2"):
            ui.label(f"Est. Slope: {proposal.estimated_slope:+.4f}").classes(
                "font-mono text-sm"
            )
            ui.label(
                f"Est. Δ Resources: {proposal.estimated_resource_delta:+.0f}"
            ).classes("font-mono text-sm")

    def _render_check_item(self, check_name: str, passed: bool) -> None:
        """Render a single constitution check item."""
        check_icon = ICONS["success"] if passed else ICONS["error"]
        check_color = "positive" if passed else "negative"
        with ui.row().classes("items-center gap-1"):
            ui.icon(check_icon).classes(f"text-{check_color} text-sm")
            ui.label(check_name.replace("_", " ").title()).classes(
                f"text-caption text-{check_color}"
            )

    def _stat_card(self, label: str, value: Any, icon: str) -> ui.element:
        with ui.card().classes("flex-1 min-w-[150px]").props("flat bordered") as card:
            ui.icon(icon).classes("text-2xl text-primary")
            ui.label(str(value)).classes("text-h4 text-bold")
            ui.label(label).classes("text-caption text-grey")
        return card

    def _refresh(self) -> None:
        """Refresh on mode change."""


def create_mutation_explorer(
    proposals: list[MutationProposal] | None = None,
    current_genome_size: int = 0,
) -> MutationExplorer:
    """Create the mutation explorer component."""
    return MutationExplorer(
        proposals=proposals, current_genome_size=current_genome_size
    )
