# Measured test walltime — committed baseline

Derived 2026-09-27 from the walltime discovery pass (TODO37 §4.11). Every
test whose call phase exceeded `WALLTIME_DISCOVERY_S = 5.0` with no declared
budget, per tier, at `-n 4` on a 24-core CUDA box. Each row became a
`@pytest.mark.timeout` next to the test and a `KNOWN_LONG` row, so the
next run of the same command is expected to report nothing.

Regenerate any tier with:

```bash
uv run python -m pytest tests/<tier> -q -n 4 --walltime-report=logs/walltime_<tier>.md
```

| seconds | tier | nodeid |
|---:|---|---|
| 27.54 | unit | `tests/unit/core/test_transformer_geometry.py::test_bp_learns_structured_tokens` |
| 15.22 | unit | `tests/unit/test_campaign_reproducibility.py::test_geometry_execution_is_bit_for_bit_reproducible` |
| 9.64 | unit | `tests/unit/core/test_campaign_stack.py::TestCampaignCLI::test_campaign_run_end_to_end` |
| 7.56 | unit | `tests/unit/core/test_nca_geometry.py::TestNcaDistillInit::test_distill_then_grow` |
| 43.65 | integration | `tests/integration/test_demo_geometry_swap.py::test_demo_geometry_swap` |
| 28.99 | integration | `tests/integration/test_continuous_burst.py::test_second_burst_never_remeasures_cells` |
| 26.65 | integration | `tests/integration/test_smoke_all_tasks.py::TestSmokeAllTasks::test_vision_kmnist` |
| 20.83 | integration | `tests/integration/test_demo_uaxis_muon_swap.py::test_demo_uaxis_muon_swap` |
| 20.58 | integration | `tests/integration/test_demo_swap_credit.py::test_demo_swap_credit` |
| 19.69 | integration | `tests/integration/test_demo_spatial_lattice_geometry_swap.py::test_demo_spatial_lattice_geometry_swap` |
| 19.12 | integration | `tests/integration/test_continuous_burst.py::test_l1_maturation_promotes_front_cells_once` |
| 16.70 | integration | `tests/integration/test_demo_temporal_psi_migration.py::test_demo_temporal_psi_migration` |
| 14.98 | integration | `tests/integration/test_demo_failure_manifesto.py::test_demo_failure_manifesto` |
| 14.92 | integration | `tests/integration/test_demo_compose_6axis.py::test_demo_compose_6axis` |
| 11.46 | integration | `tests/integration/test_demo_paxis_pareto.py::test_demo_paxis_pareto` |
| 10.38 | integration | `tests/integration/test_gallery_lock.py::test_figure_lock` |
| 7.86 | integration | `tests/integration/test_pc_alm_validation.py::TestPCALMDepthScaling::test_pcalm_depth_scaling[50]` |
| 7.62 | integration | `tests/integration/test_demo_epc_fast_settle.py::test_demo_epc_fast_settle` |
| 7.33 | integration | `tests/integration/test_pc_alm_validation.py::TestPCALMDepthScaling::test_pcalm_depth_100_no_explosion` |
| 7.30 | integration | `tests/integration/test_continuous_burst.py::test_burst_measures_cells_and_writes_artifacts` |
| 7.27 | integration | `tests/integration/test_demo_spike_settle.py::test_demo_spike_settle` |
| 37.18 | property | `tests/property/test_undefined_name_lock.py::test_every_cross_module_import_names_a_defined_symbol` |
| 6.70 | property | `tests/property/test_state_algebra_lock.py::TestSourceLock::test_type_checking_imports_are_not_called_at_runtime` |
| 5.81 | property | `tests/property/test_memory_budget_trial.py::TestFeasibilityGrid::test_never_commissionable_names_only_the_fully_walled_cells` |
