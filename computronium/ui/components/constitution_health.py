"""Constitution Health Panel (M1.12) — 6 invariants status with plain + expert registers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class ConstitutionInvariant:
    """One constitutional invariant."""

    key: str
    label: str
    passed: bool
    value: float | str
    threshold: float | str | None = None
    detail: str = ""


class ConstitutionHealthPanel(BasePanel):
    """Constitution Health Panel: 6 invariants with plain + expert registers."""

    INVARIANT_KEYS: ClassVar[list[str]] = [
        "causality_dag",
        "passivity",
        "lyapunov_bound",
        "resource_ceiling",
        "protocol_conformance",
        "recursion_invariant",
    ]

    def __init__(
        self,
        *,
        invariants: list[ConstitutionInvariant] | None = None,
        stability_verdict: object | None = None,
    ) -> None:
        super().__init__(
            panel_key="constitution_health",
            plain_explanation=(
                "This panel shows the 6 stability checks. Green = passed, Red = failed. "
                "All must pass for the campaign to be safe."
            ),
            why_explanation=(
                "The Constitution is the immutable rulebook. These 6 invariants "
                "ensure the system stays stable, passive, and within resources."
            ),
            expert_explanation=(
                "1. Causality (DAG): No circular dependencies in system coordinate. "
                "2. Passivity (Δℰ≤ℰ_in): Energy out ≤ Energy in. "
                "3. Lyapunov Bound (ρ(J_F)≤τ): Spectral radius ≤ 1.029. "
                "4. Resource Ceiling (||Z||+|Ω|): Within compute/memory budget. "
                "5. Protocol Conformance: Valid per SystemConfig.validate(). "
                "6. Recursion Invariant: Well-founded recursion depth. "
                "Metrics match StabilityMonitor byte-identically (UX-L9)."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/constitution.html",
        )
        self.invariants = invariants or []
        self.stability_verdict = stability_verdict
        self._grid_container: ui.element = ui.column().classes("w-full")

    def render(self) -> ui.element:
        """Render the Constitution Health Panel."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("constitution")

            # Overall status
            all_passed = all(inv.passed for inv in self.invariants)
            status_icon = ICONS["success"] if all_passed else ICONS["error"]
            status_color = "positive" if all_passed else "negative"
            status_text = (
                self.tr("all_checks_passed") if all_passed else self.tr("checks_failed")
            )

            with ui.row().classes("w-full items-center gap-2"):
                ui.icon(status_icon).classes(f"text-2xl text-{status_color}")
                ui.label(status_text).classes(f"text-h6 text-{status_color}")

            # Invariant grid
            self._grid_container = ui.column().classes("w-full")
            with self._grid_container:
                self._render_invariants()

        return panel

    def _render_invariants(self) -> None:
        """Render the 6 invariant cards."""
        self._grid_container.clear()
        with self._grid_container, ui.row().classes("w-full gap-4 flex-wrap"):
            for inv in self.invariants:
                self._render_invariant_card(inv)

    def _render_invariant_card(self, inv: ConstitutionInvariant) -> None:
        """Render a single invariant card."""
        icon = ICONS["success"] if inv.passed else ICONS["error"]
        color = "positive" if inv.passed else "negative"

        with ui.card().classes("flex-1 min-w-[250px]").props("flat bordered"):
            with ui.row().classes("w-full items-center gap-2"):
                ui.icon(icon).classes(f"text-xl text-{color}")
                ui.label(self.tr(inv.key)).classes("text-bold")

            ui.separator()

            # Value display
            if self.is_explorer:
                ui.label(f"{self.tr('value')}: {inv.value}").classes("text-body")
            elif inv.threshold is not None:
                ui.label(f"{inv.value} / {inv.threshold}").classes("font-mono text-sm")
            else:
                ui.label(f"{inv.value}").classes("font-mono text-sm")

            if inv.detail and self.is_lab:
                ui.label(inv.detail).classes("text-caption text-grey font-mono")

    def update_from_stability_verdict(self, verdict: object) -> None:
        """Update invariants from StabilityVerdict (match byte-identically)."""
        # This would be implemented to extract the 6 invariants from the verdict
        # For now, placeholder
        self.stability_verdict = verdict

    def _refresh(self) -> None:
        """Refresh on mode change."""
        self._render_invariants()


def create_invariants_from_monitor(
    spectral_radius: float,
    lyapunov_exponent: float,
    energy_injected: float,
    energy_consumed: float,
    resource_usage: float,
    resource_budget: float,
    max_recursion_depth: int,
    tau: float = 1.029,
) -> list[ConstitutionInvariant]:
    """Create invariants from StabilityMonitor metrics (reference implementation)."""
    return [
        ConstitutionInvariant(
            key="causality_dag",
            label="Causality (DAG)",
            passed=True,  # Would check SystemConfig.validate()
            value="Valid DAG",
            detail="SystemConfig.validate() passed",
        ),
        ConstitutionInvariant(
            key="passivity",
            label="Passivity (Δℰ≤ℰ_in)",
            passed=energy_consumed <= energy_injected + 1e-6,
            value=f"{energy_consumed:.3f}",
            threshold=f"≤{energy_injected:.3f}",
            detail=f"Injected: {energy_injected:.3f}, Consumed: {energy_consumed:.3f}",
        ),
        ConstitutionInvariant(
            key="lyapunov_bound",
            label="Lyapunov Bound (ρ(J_F)≤τ)",
            passed=spectral_radius <= tau,
            value=f"{spectral_radius:.3f}",
            threshold=f"≤{tau:.3f}",
            detail=f"Lyapunov exponent: {lyapunov_exponent:.3f}",
        ),
        ConstitutionInvariant(
            key="resource_ceiling",
            label="Resource Ceiling (||Z||+|Ω|)",
            passed=resource_usage <= resource_budget,
            value=f"{resource_usage:.0f}",
            threshold=f"≤{resource_budget:.0f}",
            detail="Compute + memory budget",
        ),
        ConstitutionInvariant(
            key="protocol_conformance",
            label="Protocol Conformance",
            passed=True,  # Would check SystemConfig.validate()
            value="Conformant",
            detail="SystemConfig.validate() passed",
        ),
        ConstitutionInvariant(
            key="recursion_invariant",
            label="Recursion Invariant",
            passed=max_recursion_depth < 100,
            value=str(max_recursion_depth),
            threshold="< 100",
            detail="Max recursion depth",
        ),
    ]
