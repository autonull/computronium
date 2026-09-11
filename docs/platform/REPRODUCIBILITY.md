# Reproducibility (T21.1.3)

Every number cited in `MANUSCRIPT.md` maps to one command and an evidence
id or registered artifact. All commands run from a fresh clone after
`uv sync --dev --all-extras` (dev-env smoke:
`uv run python -c "import optuna, scipy, torchvision, pytest"`). Budgets
are quick-mode CPU; a fresh-clone dry run completes in one session.

| Manuscript claim | Number | Command | Evidence / artifact |
|---|---|---|---|
| §3.1 frozen-null / closed-form / temporal / adaptive accuracy; θ bitwise-invariance | 0.25; 0.26; B=0.66, A-ret 0.76; B=0.74 | `uv run python packages/psi-peft/benchmarks/psi_vs_sgd_readout.py --quick` | X-TPC-001/002/003, X-TAC-001 (E-000022..E-000026) |
| §3.1 SGD readout retraining walltime ratio | ~9× | same command (timing arm) | X-TPC-003 (E-000024) |
| §3.2 late improvement-per-norm, matched norm; feedback alignment; 10-step protocol | 0.0427±0.004 vs 0.0381±0.004; 0.95 vs 0.43; 0.88/0.88/0.69 vs 0.49/0.48/0.53 | `uv run python packages/local-feedback/benchmarks/adaptive_vs_fixed.py --quick` | X-ALI-001 (E-000018), X-ALI-002 (E-000027) |
| §3.3 role-split vs parents; FF×Muon collapse | per-seed wins; collapse at width 32 | `uv run python packages/computronium-lab/examples/mechanism_recipes_demo.py` | X-USU-001 |
| §3.4 retention ratios; settle budget; paired-replay noise scaling | 4.2–5.5× / 19–40× / 940–2600×; settle 238–344 steps | `uv run python packages/computronium-lab/examples/mechanism_recipes_demo.py` (stable_amplification arm) | X-STA-001, X-STA-002 (E-000028) |
| §2 governance ledger (evidence ids, beliefs, calibration) | — | `uv run stability calibrate`-style ledger introspection via `ceec` package; ledger ships with ceec-core | E-000001..E-000028 |
| §6 package installation / gates | — | `uv sync --dev --all-extras && uv run python -m pytest tests/platform -q` | `docs/platform/RELEASE_MANIFEST.md` |

Registered artifacts referenced by the manuscript live in
`docs/figures/registered/` (manifest-locked by `docs/figures/manifest.json`;
regenerate only via the gallery lock, never by hand).

## Gate

The T21.1.3 acceptance gate is a fresh-clone dry run (no cached venv):
`git clone <repo> /tmp/rr && cd /tmp/rr && uv sync --dev --all-extras`,
then run the table's commands. Record the run in TODO21 §12.
