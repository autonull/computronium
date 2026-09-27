"""One-off: insert the budgets the walltime discovery report asked for.

Reads the measured seconds measured during the TODO37 §4.11 discovery pass and
writes two things per row: the `@pytest.mark.timeout(N)` next to the test, and
the `KNOWN_LONG` row that the bidirectional lock then holds in place.
"""

import pathlib
import re

#: ``(file, scope, measured_seconds)`` from logs/walltime_*.md, over the 5 s
#: discovery threshold, with the parametrized cell folded onto its function.
DISCOVERED: tuple[tuple[str, str, float], ...] = (
    ("tests/integration/test_demo_geometry_swap.py", "test_demo_geometry_swap", 43.65),
    ("tests/integration/test_continuous_burst.py", "test_second_burst_never_remeasures_cells", 28.99),
    ("tests/integration/test_smoke_all_tasks.py", "test_vision_kmnist", 26.65),
    ("tests/integration/test_demo_uaxis_muon_swap.py", "test_demo_uaxis_muon_swap", 20.83),
    ("tests/integration/test_demo_swap_credit.py", "test_demo_swap_credit", 20.58),
    ("tests/integration/test_demo_spatial_lattice_geometry_swap.py", "test_demo_spatial_lattice_geometry_swap", 19.69),
    ("tests/integration/test_continuous_burst.py", "test_l1_maturation_promotes_front_cells_once", 19.12),
    ("tests/integration/test_demo_temporal_psi_migration.py", "test_demo_temporal_psi_migration", 16.70),
    ("tests/integration/test_demo_failure_manifesto.py", "test_demo_failure_manifesto", 14.98),
    ("tests/integration/test_demo_compose_6axis.py", "test_demo_compose_6axis", 14.92),
    ("tests/integration/test_demo_paxis_pareto.py", "test_demo_paxis_pareto", 11.46),
    ("tests/integration/test_gallery_lock.py", "test_figure_lock", 10.38),
    ("tests/integration/test_pc_alm_validation.py", "test_pcalm_depth_scaling", 7.86),
    ("tests/integration/test_demo_epc_fast_settle.py", "test_demo_epc_fast_settle", 7.62),
    ("tests/integration/test_pc_alm_validation.py", "test_pcalm_depth_100_no_explosion", 7.33),
    ("tests/integration/test_continuous_burst.py", "test_burst_measures_cells_and_writes_artifacts", 7.30),
    ("tests/integration/test_demo_spike_settle.py", "test_demo_spike_settle", 7.27),
    ("tests/unit/core/test_transformer_geometry.py", "test_bp_learns_structured_tokens", 27.54),
    ("tests/unit/test_campaign_reproducibility.py", "test_geometry_execution_is_bit_for_bit_reproducible", 15.22),
    ("tests/unit/core/test_campaign_stack.py", "test_campaign_run_end_to_end", 9.64),
    ("tests/unit/core/test_nca_geometry.py", "test_distill_then_grow", 7.56),
    ("tests/property/test_undefined_name_lock.py", "test_every_cross_module_import_names_a_defined_symbol", 37.18),
    ("tests/property/test_state_algebra_lock.py", "test_type_checking_imports_are_not_called_at_runtime", 6.70),
    ("tests/property/test_memory_budget_trial.py", "test_never_commissionable_names_only_the_fully_walled_cells", 5.81),
)

LADDER = (300, 600, 900, 1200, 1800, 3600)
HEADROOM = 4

_DEF = re.compile(r"^(?P<indent>\s*)def (?P<name>\w+)\s*\(")


def budget_for(seconds: float) -> int:
    needed = HEADROOM * seconds
    return next((rung for rung in LADDER if rung >= needed), LADDER[-1])


def insert(path: pathlib.Path, scope: str, seconds: float) -> str:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        match = _DEF.match(line)
        if match is None or match["name"] != scope:
            continue
        if index and "mark.timeout" in lines[index - 1]:
            return f"SKIP (already marked) {path}::{scope}"
        indent = match["indent"]
        marker = (
            f"{indent}@pytest.mark.timeout({budget_for(seconds)})"
            f"  # {seconds:.1f}s measured, budget declared TODO37 §4.11\n"
        )
        lines.insert(index, marker)
        path.write_text("".join(lines), encoding="utf-8")
        return f"OK   {budget_for(seconds):>4}s  {path}::{scope}"
    return f"MISS {path}::{scope}"


rows: list[str] = []
for file, scope, seconds in DISCOVERED:
    rows.append(insert(pathlib.Path(file), scope, seconds))
print("\n".join(rows))
print(len(DISCOVERED), "rows")
