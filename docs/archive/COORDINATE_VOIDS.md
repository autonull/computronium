# Coordinate Voids — Structural Incompatibilities

This file documents structural voids (ontology boundaries, not bugs) discovered during AutoScientist campaigns. Voids are cached in the KB and skipped in subsequent runs.

## Void Categories

| Category | Description |
|----------|-------------|
| `geometry_constraint` | Geometry doesn't support dynamics' state shape |
| `credit_geometry` | Credit requires specific geometry (e.g., LocalContrastive → feedforward) |
| `dynamics_credit` | Credit incompatible with dynamics (e.g., FA on recurrent energy_min) |
| `diffusion_noise` | Diffusion requires substrate noise > 0 |

---

## Documented Voids

### PCALM × Recurrent Geometry × ThermodynamicContrast

**Coordinate**: `pc_alm | thermodynamic_contrast | * | recurrent`
**Category**: `unclassified` (shape mismatch)
**Message**: `PCALM layer 0 shape mismatch: dual_vars[0].shape=torch.Size([8, 34]) vs constraints[0].shape=torch.Size([2, 34])`
**Root Cause**: PCALM (Predictive Coding Augmented Lagrangian) credit expects a specific dual variable structure that doesn't match the recurrent geometry's layer configuration. The dual variables are shaped for batch-first feedforward layers, but recurrent geometry produces a different activation structure.
**Status**: Structural boundary — PCALM is designed for feedforward/predictive coding geometries, not recurrent attractor networks.
**Action**: Document only; do not attempt to fix. Use PCALM with feedforward or error_predictive_coding dynamics.

---

### Lazy Dynamics × Non-Feedforward Geometries

**Coordinate**: `lazy | * | * | {recurrent, tile_mesh, attention, spatial_lattice, ntm}`
**Category**: `geometry_constraint`
**Message**: `'lazy' settling feeds raw states into geometry.route(), which '{geometry}' geometry does not support (state-shape contract)` or `Recurrent geometry requires energy-based, PC-family, or instantaneous dynamics, got 'lazy'`
**Root Cause**: Lazy dynamics (sequential Gauss-Seidel EqProp) produces raw state activations that only feedforward geometries can route. Recurrent, tile_mesh, attention, spatial_lattice, and ntm geometries require specific dynamics families.
**Status**: Structural boundary — Lazy dynamics is an EqProp variant for feedforward networks only.
**Action**: Document only; lazy dynamics only works with feedforward geometry.

---

### Diffusion Dynamics × Zero-Noise Substrate

**Coordinate**: `diffusion | * | * | *` with `substrate.noise_level == 0.0`
**Category**: `diffusion_noise`
**Message**: `Diffusion dynamics (Langevin) requires substrate noise_level > 0 for proper sampling.`
**Root Cause**: Langevin dynamics requires stochastic noise for proper sampling. Digital substrate defaults to noise_level=0.0.
**Status**: Fixed in `_build_substrate_config()` — auto-sets noise_level=0.05 for diffusion dynamics.
**Action**: Auto-configured; verify spectral_radius < 1.0 in campaigns.

---

### Spatial Lattice × Default Geometry (Param Blowup)

**Coordinate**: `* | * | * | spatial_lattice` with default `lattice_dims=(4,4,4)`
**Category**: `geometry_constraint` (param budget exceeded)
**Root Cause**: Default 4×4×4 lattice (64 sites) with hidden_dim=64 produces ~3.8M parameters, far exceeding typical 25K budget.
**Status**: Fixed in `build_geometry_config()` — auto-constrains `lattice_dims` from `param_budget`.
**Action**: Auto-configured; verify param_count ≈ param_budget in campaigns.

---

## Adding New Voids

When a new structural void is discovered:

1. Run campaign to populate KB voids table
2. Query voids: `SELECT category, coordinate, message FROM structural_voids`
3. Add entry above with:
   - Coordinate pattern
   - Category
   - Root cause analysis
   - Status (fixed/structural)
   - Action taken

Voids are not failures — they are the map boundaries.