"""Workshop Panel (M3 recommendation) — the doing entry point for both audiences.

Provides:
- DialComposer: compose a 6-axis system with live compatibility feedback
- RecipeCard: try a known recipe from the recipe registry
- Fix a crash: link to Repair Bench
- Donate computer: P2P worker toggle
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nicegui import ui

from computronium.analysis.recipe_cards import RECIPE_CARDS, RecipeCard
from computronium.ontology.system import SystemConfig
from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.dynamics import StateDynamicsConfig
    from computronium.ontology.geometry import GeometryConfig
    from computronium.ontology.substrate import SubstrateConfig
    from computronium.ontology.update import ParameterUpdateConfig
    from computronium.state import PlasticityConfig


# Runtime imports for config factories
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium.state import PlasticityConfig


@dataclass(frozen=True, slots=True)
class AxisOption:
    """Single axis option for the DialComposer."""

    key: str
    label: str
    description: str
    config_factory: str  # e.g., "SubstrateConfig.digital"


# Axis option registries for DialComposer
SUBSTRATE_OPTIONS: tuple[AxisOption, ...] = (
    AxisOption(
        "digital", "Digital", "Standard digital compute", "SubstrateConfig.digital"
    ),
    AxisOption(
        "memristive",
        "Memristive",
        "Conductance with IR-drop",
        "SubstrateConfig.memristive",
    ),
    AxisOption(
        "neuromorphic",
        "Neuromorphic",
        "Spike-based async",
        "SubstrateConfig.neuromorphic",
    ),
    AxisOption(
        "optical", "Photonic", "Phase/amplitude optical", "SubstrateConfig.optical"
    ),
    AxisOption(
        "quantum", "Quantum", "Unitary gate simulation", "SubstrateConfig.quantum"
    ),
    AxisOption("sparse", "Sparse", "Structured sparsity", "SubstrateConfig.sparse"),
    AxisOption(
        "ternary", "Ternary", "Ternary weights {-α,0,+α}", "SubstrateConfig.ternary"
    ),
)

GEOMETRY_OPTIONS: tuple[AxisOption, ...] = (
    AxisOption(
        "feedforward", "Feedforward", "MLP/CNN (DAG)", "GeometryConfig.feedforward"
    ),
    AxisOption(
        "recurrent",
        "Recurrent Attractor",
        "Hopfield/EqProp",
        "GeometryConfig.recurrent",
    ),
    AxisOption("tile_mesh", "Tile Mesh", "Modular TileNet", "GeometryConfig.tile_mesh"),
    AxisOption("graph", "Graph", "Arbitrary node-edge", "GeometryConfig.graph"),
    AxisOption(
        "spatial_lattice",
        "3D Neural Cube",
        "Spatial lattice",
        "GeometryConfig.spatial_lattice",
    ),
    AxisOption("ntm", "NTM", "External memory tape", "GeometryConfig.ntm"),
    AxisOption("nca", "NCA", "Neural cellular automaton", "GeometryConfig.nca"),
)

DYNAMICS_OPTIONS: tuple[AxisOption, ...] = (
    AxisOption(
        "energy_minimization",
        "Energy Minimization",
        "EqProp settling",
        "StateDynamicsConfig.energy_minimization",
    ),
    AxisOption(
        "predictive_settling",
        "Predictive Settling",
        "Predictive Coding",
        "StateDynamicsConfig.predictive_settling",
    ),
    AxisOption(
        "spike_integration",
        "Spike Integration",
        "LIF/Izhikevich",
        "StateDynamicsConfig.spike_integration",
    ),
    AxisOption(
        "instantaneous",
        "Instantaneous Pass",
        "Single forward",
        "StateDynamicsConfig.instantaneous",
    ),
    AxisOption(
        "diffusion",
        "Diffusion",
        "Continuous diffusion",
        "StateDynamicsConfig.diffusion",
    ),
    AxisOption(
        "lazy", "Lazy (On-Demand)", "On-demand activation", "StateDynamicsConfig.lazy"
    ),
)

PLASTICITY_OPTIONS: tuple[AxisOption, ...] = (
    AxisOption("null", "Fixed Recipe", "No plasticity (5-D)", "PlasticityConfig.null"),
    AxisOption(
        "routing", "Routing", "State-dependent gating", "PlasticityConfig.routing"
    ),
    AxisOption(
        "fast_weights",
        "Fast Weights",
        "Episode-local memory",
        "PlasticityConfig.fast_weights",
    ),
    AxisOption(
        "substrate_coupled",
        "Substrate Coupled",
        "Physical plasticity",
        "PlasticityConfig.substrate_coupled",
    ),
    AxisOption(
        "rule_state", "Rule State (Z3)", "Rule selection", "PlasticityConfig.rule_state"
    ),
    AxisOption(
        "temporal_psi",
        "Temporal ψ",
        "Trace-decayed supervised",
        "PlasticityConfig.temporal_psi",
    ),
    AxisOption(
        "conflict_adaptive",
        "Conflict Adaptive",
        "Self-switching trace decay",
        "PlasticityConfig.conflict_adaptive",
    ),
)

CREDIT_OPTIONS: tuple[AxisOption, ...] = (
    AxisOption(
        "thermodynamic_contrast",
        "Thermodynamic Contrast",
        "EqProp free/nudged",
        "CreditAssignmentConfig.thermodynamic_contrast",
    ),
    AxisOption(
        "random_projections",
        "Random Projections",
        "FA/DFA fixed feedback",
        "CreditAssignmentConfig.random_projections",
    ),
    AxisOption(
        "local_goodness",
        "Local Goodness",
        "FF/PEPITA layer-local",
        "CreditAssignmentConfig.local_goodness",
    ),
    AxisOption(
        "temporal_trace",
        "Temporal Trace",
        "STDP spike timing",
        "CreditAssignmentConfig.temporal_trace",
    ),
    AxisOption(
        "target_inversion",
        "Target Inversion",
        "Target Prop",
        "CreditAssignmentConfig.target_inversion",
    ),
    AxisOption(
        "gradient", "Gradient", "Standard backprop", "CreditAssignmentConfig.gradient"
    ),
    AxisOption(
        "homeostatic",
        "Homeostatic",
        "Autonomous Lipschitz",
        "CreditAssignmentConfig.homeostatic",
    ),
)

UPDATE_OPTIONS: tuple[AxisOption, ...] = (
    AxisOption("euclidean", "Euclidean", "SGD/Adam", "ParameterUpdateConfig.euclidean"),
    AxisOption(
        "riemannian_orthogonal",
        "Riemannian Orthogonal",
        "Muon",
        "ParameterUpdateConfig.riemannian_orthogonal",
    ),
    AxisOption(
        "spectral_constrained",
        "Spectral Constrained",
        "SpectralConstrainedUpdate",
        "ParameterUpdateConfig.spectral_constrained",
    ),
    AxisOption(
        "natural_gradient",
        "Natural Gradient",
        "Fisher",
        "ParameterUpdateConfig.natural_gradient",
    ),
    AxisOption(
        "elastic_consolidation",
        "Elastic Consolidation",
        "EWC",
        "ParameterUpdateConfig.elastic_consolidation",
    ),
)


# Config factory mappings to avoid too many return statements
_SUBSTRATE_FACTORIES: dict[str, Any] = {
    "digital": lambda: SubstrateConfig.digital(device="cpu"),
    "memristive": lambda: SubstrateConfig.memristive(device="cpu"),
    "neuromorphic": lambda: SubstrateConfig.neuromorphic(device="cpu"),
    "optical": lambda: SubstrateConfig.optical(device="cpu"),
    "quantum": lambda: SubstrateConfig.quantum(device="cpu"),
    "sparse": lambda: SubstrateConfig.sparse(device="cpu"),
    "ternary": lambda: SubstrateConfig.ternary(device="cpu"),
}

_GEOMETRY_FACTORIES: dict[str, Any] = {
    "feedforward": lambda: GeometryConfig.feedforward(
        input_dim=784, output_dim=10, hidden_dims=(256, 128)
    ),
    "recurrent": lambda: GeometryConfig.recurrent(
        input_dim=784, output_dim=10, hidden_dims=(256,)
    ),
    "tile_mesh": lambda: GeometryConfig.tile_mesh(
        input_dim=784,
        output_dim=10,
        num_layers=4,
        neurons_per_tile=64,
        tiles_per_layer=4,
    ),
    "graph": lambda: GeometryConfig.graph(
        input_dim=784,
        output_dim=10,
        edge_index=[[i, i + 1] for i in range(9)],
        hidden_dims=(256,),
    ),
    "spatial_lattice": lambda: GeometryConfig.spatial_lattice(
        input_dim=784, output_dim=10, lattice_dims=(8, 8, 8)
    ),
    "ntm": lambda: GeometryConfig.ntm(
        input_dim=784, output_dim=10, hidden=32, mem_slots=16, mem_width=16
    ),
    "nca": lambda: GeometryConfig.nca(channels=32, hidden=32, grid_hw=(16, 16)),
}

_DYNAMICS_FACTORIES: dict[str, Any] = {
    "energy_minimization": lambda: StateDynamicsConfig.energy_minimization(
        max_steps=20, beta=0.5
    ),
    "predictive_settling": lambda: StateDynamicsConfig.predictive_settling(
        max_steps=20, beta=0.5
    ),
    "spike_integration": lambda: StateDynamicsConfig.spike_integration(
        max_steps=50, beta=0.5
    ),
    "instantaneous": StateDynamicsConfig.instantaneous,  # ruff: ignore[unnecessary-lambda]
    "diffusion": lambda: StateDynamicsConfig.diffusion(max_steps=100, beta=0.5),
    "lazy": lambda: StateDynamicsConfig.lazy(max_steps=10),
}

_PLASTICITY_FACTORIES: dict[str, Any] = {
    "null": PlasticityConfig.null,  # ruff: ignore[unnecessary-lambda]
    "routing": lambda: PlasticityConfig.routing(gate_dim=64),
    "fast_weights": lambda: PlasticityConfig.fast_weights(
        fast_weight_dim=512, decay=0.9, learning_rate=0.1
    ),
    "substrate_coupled": PlasticityConfig.substrate_coupled,  # ruff: ignore[unnecessary-lambda]
    "rule_state": lambda: PlasticityConfig.rule_state(num_operators=4),
    "temporal_psi": lambda: PlasticityConfig.temporal_psi(trace_decay=0.9),
    "conflict_adaptive": lambda: PlasticityConfig.conflict_adaptive(
        conflict_threshold=0.65
    ),
}

_CREDIT_FACTORIES: dict[str, Any] = {
    "thermodynamic_contrast": lambda: CreditAssignmentConfig.thermodynamic_contrast(
        beta=0.5
    ),
    "random_projections": lambda: CreditAssignmentConfig.random_projections(beta=0.5),
    "local_goodness": lambda: CreditAssignmentConfig.local_goodness(beta=0.5),
    "temporal_trace": lambda: CreditAssignmentConfig.temporal_trace(beta=0.5),
    "target_inversion": lambda: CreditAssignmentConfig.target_inversion(beta=0.5),
    "gradient": lambda: CreditAssignmentConfig.gradient(beta=0.5),
    "homeostatic": lambda: CreditAssignmentConfig.homeostatic(beta=0.5),
}

_UPDATE_FACTORIES: dict[str, Any] = {
    "euclidean": lambda: ParameterUpdateConfig.euclidean(step_size=0.01),
    "riemannian_orthogonal": lambda: ParameterUpdateConfig.riemannian_orthogonal(
        step_size=0.01
    ),
    "spectral_constrained": lambda: ParameterUpdateConfig.spectral_constrained(
        step_size=0.01
    ),
    "natural_gradient": lambda: ParameterUpdateConfig.natural_gradient(step_size=0.01),
    "elastic_consolidation": lambda: ParameterUpdateConfig.elastic_consolidation(
        step_size=0.01
    ),
}


class DialComposer:
    """6-axis system composer with live SystemConfig.validate() feedback."""

    def __init__(self) -> None:
        self._selections: dict[str, str] = {
            "substrate": "digital",
            "geometry": "feedforward",
            "dynamics": "instantaneous",
            "plasticity": "null",
            "credit": "gradient",
            "update": "euclidean",
        }
        self._status_label: Any = None
        self._detail_container: Any = None

    def render(self) -> ui.element:
        """Render the DialComposer UI."""
        with ui.card().classes("w-full") as card:
            ui.label("Build your own recipe").classes("text-h6 mb-4")

            # Axis selectors in a grid
            with ui.grid(columns=3).classes("w-full gap-4 mb-4"):
                self._render_selector("substrate", SUBSTRATE_OPTIONS, "🔩")
                self._render_selector("geometry", GEOMETRY_OPTIONS, "🔷")
                self._render_selector("dynamics", DYNAMICS_OPTIONS, "🌀")
                self._render_selector("plasticity", PLASTICITY_OPTIONS, "🧬")
                self._render_selector("credit", CREDIT_OPTIONS, "💡")
                self._render_selector("update", UPDATE_OPTIONS, "🔧")

            # Compatibility status
            with ui.row().classes("w-full items-center gap-2 mb-2"):
                ui.label("Compatibility check").classes("text-bold")
                self._status_label = ui.label("").classes("text-lg")

            # Detail container for validation messages
            self._detail_container = ui.column().classes("w-full gap-1 text-sm")

            # Initial validation
            self._validate()

        return card

    def _render_selector(
        self, axis: str, options: tuple[AxisOption, ...], icon: str
    ) -> None:
        """Render a single axis selector."""
        with ui.column().classes("gap-1"):
            ui.label(f"{icon} {axis.title()}").classes("text-bold text-sm")
            select = (
                ui
                .select(
                    options={
                        opt.key: f"{opt.label} — {opt.description}" for opt in options
                    },
                    value=self._selections[axis],
                    on_change=lambda e, a=axis: self._on_change(a, e.value),
                )
                .props("dense outlined")
                .classes("w-full")
            )
            select.tooltip(
                "\n".join(f"{opt.key}: {opt.description}" for opt in options)
            )

    def _on_change(self, axis: str, value: str) -> None:
        """Handle axis selection change."""
        self._selections[axis] = value
        self._validate()

    def _validate(self) -> None:
        """Run SystemConfig.validate() and display results."""
        config = self._build_config()
        try:
            config.validate()
        except ValueError as e:
            self._status_label.set_text("Invalid combination")
            self._status_label.classes(remove="text-positive", add="text-negative")
            self._detail_container.clear()
            with self._detail_container:
                ui.label(str(e)).classes("text-negative text-sm font-mono")
            return
        except Exception as e:  # ruff: ignore[blind-except]
            self._status_label.set_text("Validation error")
            self._status_label.classes(remove="text-positive", add="text-warning")
            self._detail_container.clear()
            with self._detail_container:
                ui.label(f"Unexpected error: {e}").classes("text-warning text-sm")
            return

        self._status_label.set_text("Valid combination")
        self._status_label.classes(remove="text-negative", add="text-positive")
        self._detail_container.clear()
        with self._detail_container:
            ui.label("All cross-axis constraints satisfied").classes(
                "text-positive text-sm"
            )

    def _build_config(self) -> SystemConfig:
        """Build a SystemConfig from current selections."""
        substrate = self._make_config("substrate", _SUBSTRATE_FACTORIES)
        geometry = self._make_config("geometry", _GEOMETRY_FACTORIES)
        dynamics = self._make_config("dynamics", _DYNAMICS_FACTORIES)
        plasticity = self._make_config("plasticity", _PLASTICITY_FACTORIES)
        credit = self._make_config("credit", _CREDIT_FACTORIES)
        update = self._make_config("update", _UPDATE_FACTORIES)

        return SystemConfig(
            substrate=substrate,
            geometry=geometry,
            dynamics=dynamics,
            credit=credit,
            update=update,
            plasticity=plasticity,
        )

    def _make_config(self, axis: str, factories: dict[str, Any]) -> Any:
        """Create config using factory mapping."""
        key = self._selections[axis]
        factory = factories.get(key)
        if factory is None:
            # Fallback to first option
            factory = next(iter(factories.values()))
        return factory()


class RecipeCardPanel:
    """Display known recipe cards from the registry."""

    def __init__(self) -> None:
        self._cards = list(RECIPE_CARDS.items())

    def render(self) -> ui.element:
        """Render the recipe card gallery."""
        with ui.card().classes("w-full") as card:
            ui.label("Try a known recipe").classes("text-h6 mb-4")

            with ui.row().classes("w-full flex-wrap gap-4"):
                for (family, update), recipe in self._cards:
                    self._render_recipe_card(family, update, recipe)

        return card

    def _render_recipe_card(self, family: str, update: str, recipe: RecipeCard) -> None:
        """Render a single recipe card."""
        status_colors = {
            "rescue": "positive",
            "rescue_sharp": "positive",
            "home": "primary",
            "harm": "negative",
            "closed": "grey",
            "boundary": "warning",
            "peak_collapse": "warning",
            "depth_wall_d2": "warning",
        }
        color = status_colors.get(recipe.status, "grey")

        with ui.card().classes("w-64"):
            ui.label(f"{family} × {update}").classes("text-bold")
            ui.badge(recipe.status.replace("_", " ").title(), color=color).classes(
                "mb-2"
            )

            if recipe.parity is not None:
                ui.label(f"BP Parity: {recipe.parity:.1%}").classes("text-sm")
            if recipe.delta is not None:
                delta_color = "text-positive" if recipe.delta > 0 else "text-negative"
                ui.label(f"Δ vs BP: {recipe.delta:+.2f}").classes(
                    f"text-sm {delta_color}"
                )
            if recipe.mechanism:
                ui.label(f"Mechanism: {recipe.mechanism}").classes(
                    "text-caption text-grey"
                )
            if recipe.geometries:
                ui.label(f"Geometries: {', '.join(recipe.geometries)}").classes(
                    "text-caption text-grey"
                )
            if recipe.edge:
                ui.label(f"Edge: {recipe.edge}").classes("text-caption text-grey")


class P2PToggle:
    """P2P worker toggle for donating compute."""

    def __init__(self) -> None:
        self._running = False

    def render(self) -> ui.element:
        """Render the P2P toggle."""
        with (
            ui.card().classes("w-full") as card,
            ui.row().classes("w-full items-center justify-between"),
        ):
            with ui.column().classes("gap-1"):
                ui.label("Donate computer").classes("text-h6")
                ui.label(
                    "Run a P2P worker to contribute compute to the network"
                ).classes("text-body text-grey")

            ui.switch(
                "Run worker",
                value=self._running,
                on_change=self._on_toggle,
            ).props("size=md")
        return card

    def _on_toggle(self, e: Any) -> None:
        """Handle toggle change."""
        self._running = e.value
        if self._running:
            ui.notify("Starting P2P worker... (not implemented in demo)", type="info")
        else:
            ui.notify("Stopping P2P worker...", type="info")


class WorkshopPanel(BasePanel):
    """Workshop panel — the doing entry point.

    Tabs:
    - Build your own (DialComposer)
    - Try a known recipe (RecipeCard)
    - Fix a crash (links to Repair Bench)
    - Donate computer (P2P toggle)
    """

    def __init__(self) -> None:
        super().__init__(
            panel_key="workshop",
            plain="The workshop is where you build and try learning recipes. You can compose your own from the 6-axis menu, pick a known recipe card, or help fix crashes.",
            why="Learning systems are built from 6 independent choices (substrate, geometry, dynamics, plasticity, credit, update). The workshop lets you explore this space hands-on — with live compatibility checks so you only build valid combinations.",
            expert="DialComposer provides a SystemConfig.validate()-backed compatibility matrix across S×G×D×M×C×U axes. RecipeCards surface measurement-backed verdicts from the I(C,U) ladder (TODO16 §0.3). P2P toggle launches a gRPC worker (computronium.p2p.grpc_worker) for distributed burst execution.",
            docs_url="https://github.com/computronium/computronium/blob/main/docs/platform/workshop.md",
        )
        self._dial_composer = DialComposer()
        self._recipe_card = RecipeCardPanel()
        self._p2p_toggle = P2PToggle()

    def render(self) -> ui.element:
        """Render the workshop panel with tabs."""
        with ui.column().classes("w-full") as container:
            self.render_header("Workshop")

            with ui.tabs().classes("w-full") as tabs:
                tab_composer = ui.tab("Build your own recipe", icon="tune")
                tab_recipe = ui.tab("Try a known recipe", icon="menu_book")
                tab_repair = ui.tab("Fix a crash", icon="build")
                tab_p2p = ui.tab("Donate computer", icon="computer")

            with ui.tab_panels(tabs, value=tab_composer).classes("w-full"):
                with ui.tab_panel(tab_composer):
                    self._dial_composer.render()

                with ui.tab_panel(tab_recipe):
                    self._recipe_card.render()

                with ui.tab_panel(tab_repair):
                    self._render_repair_link()

                with ui.tab_panel(tab_p2p):
                    self._p2p_toggle.render()

        return container

    def _render_repair_link(self) -> None:
        """Render link to Repair Bench."""
        with ui.card().classes("w-full"):
            ui.label("Fix a crash").classes("text-h6 mb-4")
            ui.label(
                "Found a crash? The Repair Bench shows all quarantined defects with "
                "copy-pasteable unquarantine commands."
            ).classes("text-body text-grey mb-4")
            ui.button(
                "Open Repair Bench",
                icon="arrow_forward",
                on_click=lambda: ui.navigate.to("#repair-bench"),
            ).props("color=primary")


def create_workshop_panel() -> WorkshopPanel:
    """Factory function for WorkshopPanel."""
    return WorkshopPanel()


__all__ = [
    "CREDIT_OPTIONS",
    "DYNAMICS_OPTIONS",
    "GEOMETRY_OPTIONS",
    "PLASTICITY_OPTIONS",
    "SUBSTRATE_OPTIONS",
    "UPDATE_OPTIONS",
    "AxisOption",
    "DialComposer",
    "P2PToggle",
    "RecipeCardPanel",
    "WorkshopPanel",
    "create_workshop_panel",
]
