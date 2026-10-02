## 6. CLI reference

`comp <command>` — every subcommand either works end-to-end or does not exist in the dispatcher:

<!-- gen:cli_table -->

This table is locked against the dispatcher by `tests/property/test_cli_readme_lock.py` — set and purpose lines must match exactly, and every fenced `bash` block in this README is executed by that lock, so a documented invocation that errors fails CI.

Kernel operations:

```bash
uv run comp --help                    # every command above
uv run comp run quick-verify --dry-run   # resolve the plan; writes nothing
uv run comp run quick-verify --store experiment.duckdb
uv run comp status --store experiment.duckdb
uv run comp report --run-id <id> --store experiment.duckdb
```

---
