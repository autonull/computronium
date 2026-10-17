## Start here

Six commands, no second document.

```bash
uv sync --dev --all-extras
uv run comp run demo --dry-run          # the declared space, priced
uv run comp demo --store demo.duckdb    # seven beats: space, run, ledger, report, coverage, results
uv run comp report --store demo.duckdb --format text
uv run comp coverage report --store demo.duckdb
uv run comp --help                      # core commands; --help-all shows every command
```

What comes out:

- a controlled contrast — five of six axes fixed, one varied — with `n`, `std`
  and an `[at chance]` flag on every row;
- claims with `n` and variance, and limitations that name the filter which
  re-derives them (`[insufficient_power]`, `[unpreregistered_claim]`,
  `[cells_abandoned]`, …);
- a verdict of `PASSED`, `REJECTED`, or `INSUFFICIENT`, with `power_achieved`;
- the price of a real answer: 63 seeds per group for a d=0.5 effect, times
  every arm and every axis.

The demo does not promise a win. It promises a protocol: the control arm must
clear chance before a comparison is published, and an underpowered run says so
instead of declaring "no effect".

The Python library is separate and usable on its own — see
[Machine learning library](#machine-learning-library) below, or run the
60-second snippet it contains.

A six-minute shot list — every command and the sentence to say over it — is in
[`docs/DEMO.md`](docs/DEMO.md); `tests/acceptance/test_demo_script.py` runs the
same commands, so the recording cannot drift from the software.
