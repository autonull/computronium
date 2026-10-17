## 📋 Architecture Cheatsheet

![Computronium Architecture Cheatsheet](docs/cheatsheet/cheatsheet.svg)

Computronium at a glance — a live reflection of the codebase architecture, regenerated from source on every build.

### Outer Flow

```
Entry Points → Tasks & Data → Experiment Kernel → 6-Axis Ontology → System Composition → Training Loop → Evidence Store → Surface & Governance
              ↑_______________________________________________________________________________________________________|
                                    🔁 evidence → next question
```

### Panels Summary

| Panel | Key Contents |
|-------|--------------|
| **🚪 Entry Points** | <!-- gen:cli_count --> subcommands, <!-- gen:api_count --> Python API symbols, <!-- gen:demo_count --> demos + <!-- gen:gallery_count --> gallery figures |
| **🎯 Tasks & Data** | <!-- gen:domain_count --> domains, <!-- gen:task_count --> tasks |
| **🧪 Experiment Kernel** | <!-- gen:stage_count --> pipeline stages, <!-- gen:policy_count --> policies, <!-- gen:objective_count --> objectives (<!-- gen:measured_objective_count --> measured), <!-- gen:prior_count --> priors, <!-- gen:capability_count --> capabilities, <!-- gen:constraint_count --> constraints |
| **🧬 6-Axis Ontology** | <!-- gen:substrate_count --> substrates, <!-- gen:geometry_count --> geometries, <!-- gen:dynamics_count --> dynamics, <!-- gen:plasticity_count --> plasticities, <!-- gen:credit_count --> credits, <!-- gen:update_count --> updates = <!-- gen:primitive_total --> primitives |
| **🏗️ System & Composition** | 6-axis config × SystemTrainerConfig (<!-- gen:trainer_config_fields --> fields), `compose_joint_system` factory |
| **⚡ Training Loop** | Epoch history: train_acc, train_energy, train_loss, val_acc, val_loss + evaluator adds param_count, walltime_s |
| **💾 Evidence Store** | DuckDB, single-writer, <!-- gen:store_method_count --> RecordStore methods, schema v<!-- gen:schema_version --> with <!-- gen:record_field_count --> fields, 3-tier claim status |
| **📊 Surface & Governance** | 5 verification levels (L1–L5), <!-- gen:package_count --> workspace packages, `comp report/export/conformance/status` |

### Artifacts

- **SVG diagram**: [`docs/cheatsheet/cheatsheet.svg`](docs/cheatsheet/cheatsheet.svg) — directed architecture graph with nested panel insets
- **Data file**: [`docs/cheatsheet/cheatsheet.txt`](docs/cheatsheet/cheatsheet.txt) — structured data behind the diagram

> **Regeneration**: `uv run python docs/cheatsheet/cheatsheet_create.py` — pulls live facts from registries, configs, and catalogs.