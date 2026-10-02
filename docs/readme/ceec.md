---

## 🧭 CEEC Epistemic Operating System (`packages/ceec-core`)

**Standalone** epistemic governance ledger (TODO19 Epistemic Foundry) — not integrated into the experiment kernel. The kernel records a `ceec_link` field on claims (always `None` currently) for future integration.

`Experiment → Artifact → Evidence → Derived → Belief → Gated Status → Decision`.
**Full reference: [`CEEC.md`](CEEC.md)** — policies in `docs/ceec/`.

| Module (`ceec.*`) | Purpose |
|--------|---------|
| `store.py` | Append-only SQLite ledger; content-addressed artifacts; DB-trigger immutability |
| `gates.py` | Promotion/boundary gate engine, quarantine propagation, effective-status resolution |
| `selection.py` | EV/cost experiment selection with pre-scoring hard-constraint filter and audited decisions |
| `calibration.py` | Brier/log-score calibration, drift cadence, review flags |
| `builders.py` | Payload builders: `experiment`, `gate_evidence`/`quality_flags`, `chance_verdict` |
| `run.py` | Closed-loop runner `run_experiment`: pre-register → decide → probe → calibrate → optional gate |
| `audit.py` | Ledger integrity audit + decision-quality audit |
| `bootstrap.py` | Seeds instruments, hypotheses, goals, pre-registered experiments from `configs/ceec/` |
| `schemas.py` | Mechanism-schema emission from gated evidence |
| `probe_adapter.py` / `constraints.py` / `migrate/` / `cli.py` | Probe ingestion, constraint validators, migration, CLI |

CLI: `ceec init|bootstrap|migrate|propose|decide|audit|calibration-report|status-history|quarantine-report|emit-schema|export`
(or `uv run python -m ceec.cli`; `computronium/ceec/` is a legacy re-export
shim of this package). Main ledger at `ceec/ceec.sqlite3`; campaign
ledgers under `scratch/`.

---

## 📦 Standalone Platform Packages (`packages/`)

Extracted, framework-free packages the repo depends on (uv workspace
members, TODO20 Rule 6 — one implementation copy each; legacy
`computronium.*` import paths are thin adapters):

| Package | Import | What it is |
|---|---|---|
| `packages/ceec-core` | `ceec` | Standalone epistemic governance ledger (evidence/beliefs/gates/audit — **reference: [`CEEC.md`](CEEC.md)**); payload builders + closed-loop runner (`ceec.builders`/`ceec.run`); CLI `ceec` |
| `packages/psi-peft` | `psi_peft` | Frozen-backbone task switching via temporal-ψ ridge readouts |
| `packages/local-feedback` | `local_feedback` | Adaptive local feedback projections for local credit (X-ALI-001/002 validated) |
| `packages/computronium-lab` | `computronium_lab` | Standalone high-level Lab API (used in probe scripts): compose/train/compare/report ontology coordinates + mechanism recipes; synthesis layer (`Lab.specify/synthesize/explore`), task tiers, validation campaigns, research layer (budgeted evolution, certified corpus, continual benchmark), instrument layer (ledger report renderer, one-shot research report) |
| `packages/stability` | `stability` | Calibrated stability guard (`attach`, ROC-calibrated τ=1.029); stable-matrix helpers; CLI `stability` |

Platform docs (recipe book, edge blueprint, external summary, release
notes/manifest): `docs/platform/`. X-STA-002 validated the
stable-amplification family: 4×–2600× transient retention over matched
contractive controls at ρ=0.85, noise amplified at the same rate (retention
gain, not SNR gain); shipped as the Lab `stable_amplification` recipe.

`uv sync` installs them as editable workspace members automatically.