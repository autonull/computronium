"""Advanced Analyses & Visualizations (Phase D of TODO55).

Provides sophisticated analyses for experimental campaigns:
- Energy landscape analysis (2D PCA slices)
- Nonnormality analysis (pseudospectra, transient amplification)
- Axis attribution (SHAP/ICE for ontology axes)
- Counterfactual trajectories
- Mediation analysis
- Gradient statistics
- Weight evolution
- Pareto front analysis (interactive, scalarization, hypervolume)
- Seed variability analysis
- Hardware variance analysis
- Reproducibility verification
"""

from __future__ import annotations

from .axis_attribution import (
    AttributionConfig,
    AxisAttributionAnalyzer,
    analyze_axis_importance,
    compute_ice_curves,
    compute_shap_attribution,
)
from .counterfactual import (
    CounterfactualAnalyzer,
    CounterfactualConfig,
    analyze_counterfactuals,
    compute_counterfactual_trajectory,
)
from .energy_landscape import (
    EnergyLandscapeAnalyzer,
    EnergyLandscapeConfig,
    compute_energy_landscape_2d,
    plot_energy_landscape,
)
from .gradient_stats import (
    GradientStatsAnalyzer,
    compute_gradient_cosine_similarity,
    compute_gradient_statistics,
    compute_layer_alignment,
)
from .hardware_variance import (
    HardwareVarianceAnalyzer,
    compare_hardware_performance,
)
from .mediation import (
    MediationAnalyzer,
    analyze_mediation,
)
from .nonnormality import (
    NonnormalityAnalyzer,
    NonnormalityConfig,
    analyze_nonnormality,
    compute_pseudospectrum,
    compute_transient_amplification_bounds,
)
from .pareto_analysis import (
    ParetoAnalyzer,
    ParetoConfig,
    compute_hypervolume,
    compute_pareto_frontier,
    compute_scalarization_sweep,
)
from .reproducibility import (
    ReproducibilityAnalyzer,
    ReproducibilityConfig,
    verify_bitwise_reproducibility,
    verify_checkpoint_replay,
)
from .seed_variability import (
    SeedVariabilityAnalyzer,
    SeedVariabilityConfig,
    compute_seed_variability,
    plot_violin_plots,
)
from .weight_evolution import (
    WeightEvolutionAnalyzer,
    compute_effective_rank,
    compute_plasticity_metrics,
    compute_weight_spectral_norm,
)

__all__ = [
    "AttributionConfig",
    # Axis attribution
    "AxisAttributionAnalyzer",
    # Counterfactual
    "CounterfactualAnalyzer",
    "CounterfactualConfig",
    # Energy landscape
    "EnergyLandscapeAnalyzer",
    "EnergyLandscapeConfig",
    # Gradient stats
    "GradientStatsAnalyzer",
    # Hardware variance
    "HardwareVarianceAnalyzer",
    # Mediation
    "MediationAnalyzer",
    # Nonnormality
    "NonnormalityAnalyzer",
    "NonnormalityConfig",
    # Pareto
    "ParetoAnalyzer",
    "ParetoConfig",
    # Reproducibility
    "ReproducibilityAnalyzer",
    "ReproducibilityConfig",
    # Seed variability
    "SeedVariabilityAnalyzer",
    "SeedVariabilityConfig",
    # Weight evolution
    "WeightEvolutionAnalyzer",
    "analyze_axis_importance",
    "analyze_counterfactuals",
    "analyze_mediation",
    "analyze_nonnormality",
    "compare_hardware_performance",
    "compute_counterfactual_trajectory",
    "compute_effective_rank",
    "compute_energy_landscape_2d",
    "compute_gradient_cosine_similarity",
    "compute_gradient_statistics",
    "compute_hypervolume",
    "compute_ice_curves",
    "compute_layer_alignment",
    "compute_pareto_frontier",
    "compute_plasticity_metrics",
    "compute_pseudospectrum",
    "compute_scalarization_sweep",
    "compute_seed_variability",
    "compute_shap_attribution",
    "compute_transient_amplification_bounds",
    "compute_weight_spectral_norm",
    "plot_energy_landscape",
    "plot_violin_plots",
    "verify_bitwise_reproducibility",
    "verify_checkpoint_replay",
]
