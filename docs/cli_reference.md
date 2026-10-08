# CLI Reference

Auto-generated from `comp --help` output.

## Main Command

```
usage: comp [-h] <command> ...

Computronium — experiment surface over the Kernel and Library.

positional arguments:
  <command>
    run                 Execute a run profile (dry-run with --dry-run)
    report              Generate report from store
    export              Export store data for round-trip
    conformance         Check capability conformance
    status              Show run/store status
    gallery             Render gallery figures from demo records
    hypothesis-campaign
                        Run hypothesis templates over campaign records
    stability-plasticity
                        Generate and run stability-plasticity frontier
                        campaign
    frozen-theta-psi    Run frozen-θ ψ benchmarks at scale (multi-substrate,
                        multi-plasticity)
    parity              Check library-vs-kernel parity for an axis
    repro               Replay a recorded run and diff it
    validate            Validate a config or record against the schema
    joint-validate      Validate a composed multi-axis system
    benchmark           Run kernel benchmarks and emit a verdict
    stats               Compute summary statistics for run metrics (machine-
                        readable)
    pareto              Export Pareto frontier for plotting (machine-readable)
    diff                Statistical run comparison with effect sizes
    campaign            Run declarative multi-run YAML campaigns
    schema              Dump JSON schemas for RunSpec/Coordinate/Objectives

options:
  -h, --help            show this help message and exit

Run 'comp <command> --help' for that command's own options.
```

## `comp run`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface run [-h] [--store STORE] [--device {auto,cpu,cuda}]
                        [--run-id RUN_ID] [--spec SPEC] [--task TASK]
                        [--overrides OVERRIDES] [--dry-run]
                        [--format {json,text}] [--output OUTPUT]
                        [{quick-verify,production-map,maturation,claim}]

positional arguments:
  {quick-verify,production-map,maturation,claim}
                        Run profile to execute (omit when --spec names the
                        run)

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --device {auto,cpu,cuda}
                        Device to run on: auto (CUDA if available), cpu, cuda
  --run-id RUN_ID       Resume this run: the store is the checkpoint, so a
                        relaunch measures only what the run has not
  --spec SPEC           RunSpec JSON file
  --task TASK           Override the profile's task (ignored with --spec)
  --overrides OVERRIDES
                        JSON overrides for profile parameters
  --dry-run             Print plan without executing
  --format {json,text}  Output format
  --output OUTPUT       Output file path
```

## `comp report`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface report [-h] [--store STORE] [--run-id RUN_ID]
                           [--format {text,json,parquet,html,latex,pdf}]
                           [--output OUTPUT] [--axis-coverage] [--keep-tex]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to report on (latest if omitted)
  --format {text,json,parquet,html,latex,pdf}
                        Output format
  --output OUTPUT       Output file path
  --axis-coverage       Show per-axis stratification of records (R18 axis-
                        coverage section)
  --keep-tex            Keep intermediate .tex file when generating PDF
```

## `comp export`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface export [-h] [--store STORE] [--run-id RUN_ID]
                           [--format {json,parquet}] --output OUTPUT
                           [--docker]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to export (all if omitted)
  --format {json,parquet}
                        Export format
  --output OUTPUT       Output file/directory path
  --docker              Generate Dockerfile for reproducible environment
```

## `comp conformance`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface conformance [-h] [--store STORE] [--run-id RUN_ID]
                                [--list-only] [--dry-run]
                                [--format {json,text}] [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to check
  --list-only           List capabilities without checking
  --dry-run             Show plan without executing
  --format {json,text}  Output format
  --output OUTPUT       Output file path
```

## `comp status`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface status [-h] [--store STORE] [--run-id RUN_ID] [--detailed]
                           [--dry-run] [--format {json,text}]
                           [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to check (all if omitted)
  --detailed            Show campaign economics: cost per record, projected
                        completion
  --dry-run             Show plan without executing
  --format {json,text}  Output format
  --output OUTPUT       Output file path
```

## `comp gallery`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface gallery [-h] [--records-dir RECORDS_DIR]
                            [--output-dir OUTPUT_DIR] [--dry-run]
                            [--format {json,text}] [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  --records-dir RECORDS_DIR
                        Directory containing demo run records
  --output-dir OUTPUT_DIR
                        Output directory for gallery figures
  --dry-run             Show plan without executing
  --format {json,text}  Output format
  --output OUTPUT       Output file path
```

## `comp hypothesis-campaign`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface hypothesis-campaign [-h] [--store STORE] [--run-id RUN_ID]
                                        --templates TEMPLATES
                                        [--output OUTPUT]
                                        [--format {json,text}] [--dry-run]
                                        [--bind BIND]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to evaluate (latest if omitted)
  --templates TEMPLATES
                        JSON file with hypothesis templates
  --output OUTPUT       Output file for results (JSON)
  --format {json,text}  Output format
  --dry-run             Show plan without executing
  --bind BIND           Parameter bindings for templates (format:
                        template_name:param=value)
```

## `comp stability-plasticity`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface stability-plasticity [-h] [--store STORE]
                                         [--output-spec OUTPUT_SPEC]
                                         [--rho RHO]
                                         [--feedback-scale FEEDBACK_SCALE]
                                         [--precision PRECISION]
                                         [--noise-level NOISE_LEVEL]
                                         [--convergence-start CONVERGENCE_START]
                                         [--seeds SEEDS] [--epochs EPOCHS]
                                         [--budget-seconds BUDGET_SECONDS]
                                         [--run] [--dry-run]
                                         [--format {json,text}]
                                         [--output OUTPUT] [--run-id RUN_ID]
                                         [--axis-substrate AXIS_SUBSTRATE]
                                         [--axis-geometry AXIS_GEOMETRY]
                                         [--axis-dynamics AXIS_DYNAMICS]
                                         [--axis-plasticity AXIS_PLASTICITY]
                                         [--axis-credit AXIS_CREDIT]
                                         [--axis-update AXIS_UPDATE]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --output-spec OUTPUT_SPEC
                        Output path for generated RunSpec (JSON)
  --rho RHO             Rho (contraction) values (comma-separated)
  --feedback-scale FEEDBACK_SCALE
                        Feedback scale (coupling) values (comma-separated)
  --precision PRECISION
                        Precision levels (comma-separated)
  --noise-level NOISE_LEVEL
                        Noise level values (comma-separated)
  --convergence-start CONVERGENCE_START
                        Convergence start (delay proxy) values (comma-
                        separated)
  --seeds SEEDS         Seeds per coordinate
  --epochs EPOCHS       Epochs per run (L1 fidelity)
  --budget-seconds BUDGET_SECONDS
                        Budget in seconds
  --run                 Run the campaign after generating spec
  --dry-run             Show plan without running
  --format {json,text}  Output format
  --output OUTPUT       Output file path
  --run-id RUN_ID       Resume an existing run instead of starting a new one
  --axis-substrate AXIS_SUBSTRATE
                        Substrate primitives (comma-separated; default:
                        digital)
  --axis-geometry AXIS_GEOMETRY
                        Geometry primitives (comma-separated; default:
                        recurrent)
  --axis-dynamics AXIS_DYNAMICS
                        Dynamics primitives (comma-separated; default:
                        energy_minimization)
  --axis-plasticity AXIS_PLASTICITY
                        Plasticity primitives (comma-separated; default: null)
  --axis-credit AXIS_CREDIT
                        Credit primitives (comma-separated; default:
                        thermodynamic_contrast)
  --axis-update AXIS_UPDATE
                        Update primitives (comma-separated; default:
                        euclidean)
```

## `comp frozen-theta-psi`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface frozen-theta-psi [-h] [--store STORE]
                                     [--output-dir OUTPUT_DIR]
                                     [--substrates SUBSTRATES]
                                     [--plasticity-types PLASTICITY_TYPES]
                                     [--geometry GEOMETRY]
                                     [--dynamics DYNAMICS] [--credit CREDIT]
                                     [--update UPDATE] [--epochs EPOCHS]
                                     [--recovery-steps RECOVERY_STEPS]
                                     [--damage-severity DAMAGE_SEVERITY]
                                     [--seeds SEEDS] [--device DEVICE] [--run]
                                     [--dry-run] [--format {json,text}]
                                     [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --output-dir OUTPUT_DIR
                        Output directory for results
  --substrates SUBSTRATES
                        Substrates to test (comma-separated)
  --plasticity-types PLASTICITY_TYPES
                        Plasticity types to test (comma-separated)
  --geometry GEOMETRY   Geometry primitive
  --dynamics DYNAMICS   Dynamics primitive
  --credit CREDIT       Credit primitive
  --update UPDATE       Update primitive
  --epochs EPOCHS       Pre-training epochs (L2 fidelity)
  --recovery-steps RECOVERY_STEPS
                        Recovery training steps
  --damage-severity DAMAGE_SEVERITY
                        Damage severity (0-1)
  --seeds SEEDS         Number of seeds
  --device DEVICE       Device (auto, cpu, cuda)
  --run                 Run the benchmark
  --dry-run             Show plan without running
  --format {json,text}  Output format
  --output OUTPUT       Output file path
```

## `comp parity`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp parity [-h] [--config-a CONFIG_A] [--config-b CONFIG_B]
                   [--task TASK] [--epochs EPOCHS] [--lr LR]
                   [--hidden HIDDEN_DIM] [--seed SEED] [--device DEVICE]
                   [--json]

``comp-parity`` — Backprop-baseline parity CLI.

options:
  -h, --help           show this help message and exit
  --config-a CONFIG_A  First config (baseline)
  --config-b CONFIG_B  Second config (compare)
  --task TASK
  --epochs EPOCHS
  --lr LR
  --hidden HIDDEN_DIM
  --seed SEED
  --device DEVICE
  --json
```

## `comp repro`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface repro [-h] [--store STORE] --run-id RUN_ID
                          [--tolerance TOLERANCE] [--metrics METRICS]
                          [--seeds SEEDS] [--device DEVICE]
                          [--format {json,text}] [--output OUTPUT] [--docker]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to reproduce
  --tolerance TOLERANCE
                        Numerical tolerance for bitwise match
  --metrics METRICS     Comma-separated metrics to verify (all measured if
                        omitted)
  --seeds SEEDS         Override seed count for repro run
  --device DEVICE       Device for repro run (auto, cpu, cuda)
  --format {json,text}  Output format
  --output OUTPUT       Output file path
  --docker              Run reproduction in Docker container
```

## `comp validate`

```
usage: comp validate [-h] [--quick] [--intermediate] [--full] [--seed SEED]
                     [--tracks TRACKS] [--output-dir OUTPUT_DIR] [--parallel]
                     [--list]

Run validation tracks and record to knowledge base

options:
  -h, --help            show this help message and exit
  --quick               Quick mode (smoke test, ~2 min)
  --intermediate        Intermediate mode (directional, ~1 hour)
  --full                Full mode (statistically significant, ~4+ hr)
  --seed SEED           Random seed
  --tracks TRACKS       Comma-separated track IDs to run (default: all)
  --output-dir OUTPUT_DIR
                        Output directory for verification notebook
  --parallel            Run tracks in parallel
  --list                List available tracks and exit
```

## `comp joint-validate`

```
usage: comp joint-validate [-h] [--coordinate COORDINATE] [--list-axes]
                           [--quick] [--composability] [--adapters]
                           [--plasticity] [--seed SEED]
                           [--num-samples NUM_SAMPLES]

Validate 6-D joint architecture coordinates against property locks

options:
  -h, --help            show this help message and exit
  --coordinate COORDINATE
                        6-D coordinate string:
                        substrate/geometry/dynamics/plasticity/credit/update
                        (e.g.,
                        digital/recurrent/energy_min/null/thermo/euclidean)
  --list-axes           List available axis options and exit
  --quick               Quick validation (lifecycle locks only, ~30 sec)
  --composability       Test random composability (generate 10 random valid
                        coordinates)
  --adapters            Test adapter projections for the coordinate
  --plasticity          Test plasticity axis certification
  --seed SEED           Random seed for composability tests
  --num-samples NUM_SAMPLES
                        Number of random coordinates to test for composability
```

## `comp benchmark`

```
usage: comp benchmark [-h] {run,list,report,compare,profile} ...

Run joint architecture benchmark suites

positional arguments:
  {run,list,report,compare,profile}
                        Benchmark subcommand
    run                 Run a benchmark suite
    list                List available benchmark suites
    report              Generate benchmark report
    compare             Compare plasticity types
    profile             Profile joint system kernels

options:
  -h, --help            show this help message and exit
```

## `comp stats`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface stats [-h] [--store STORE] [--run-id RUN_ID]
                          [--metrics METRICS] [--agg AGG]
                          [--group-by GROUP_BY] [--format {json,csv,table}]
                          [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to analyze (latest if omitted)
  --metrics METRICS     Comma-separated metrics to compute statistics for
  --agg AGG             Comma-separated aggregations:
                        mean,std,min,max,median,ci95,count
  --group-by GROUP_BY   Comma-separated axes to group by (e.g.,
                        credit,update,substrate)
  --format {json,csv,table}
                        Output format
  --output OUTPUT       Output file path
```

## `comp pareto`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface pareto [-h] [--store STORE] [--run-id RUN_ID]
                           [--objectives OBJECTIVES] [--maximize MAXIMIZE]
                           [--format {json,csv}] --output OUTPUT

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id RUN_ID       Run ID to analyze (latest if omitted)
  --objectives OBJECTIVES
                        Comma-separated objectives for frontier (2+
                        objectives)
  --maximize MAXIMIZE   Comma-separated maximize flags (true/false per
                        objective, auto-detected if omitted)
  --format {json,csv}   Output format
  --output OUTPUT       Output file path
```

## `comp diff`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface diff [-h] [--store STORE] --run-id-a RUN_ID_A
                         --run-id-b RUN_ID_B [--metrics METRICS]
                         [--test {ttest,wilcoxon,mannwhitney}]
                         [--format {json,table}] [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path
  --run-id-a RUN_ID_A   First run ID
  --run-id-b RUN_ID_B   Second run ID
  --metrics METRICS     Comma-separated metrics to compare
  --test {ttest,wilcoxon,mannwhitney}
                        Statistical test
  --format {json,table}
                        Output format
  --output OUTPUT       Output file path
```

## `comp campaign`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface campaign [-h] [--store STORE] [--parallel PARALLEL]
                             [--device DEVICE] [--webhook-url WEBHOOK_URL]
                             [--dry-run] [--output OUTPUT]
                             [--format {json,text}]
                             campaign_file

positional arguments:
  campaign_file         Path to campaign YAML file

options:
  -h, --help            show this help message and exit
  --store STORE         DuckDB store path (overrides campaign file)
  --parallel PARALLEL   Number of parallel runs (overrides campaign file)
  --device DEVICE       Device for all runs: auto, cpu, cuda (overrides
                        campaign file)
  --webhook-url WEBHOOK_URL
                        Webhook URL for progress notifications (overrides
                        campaign file)
  --dry-run             Validate campaign file and print execution plan
                        without running
  --output OUTPUT       Output file for campaign results (JSON)
  --format {json,text}  Output format
```

## `comp schema`

```
/home/me/computronium/.venv/lib/python3.14/site-packages/torch/cuda/__init__.py:68: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
usage: comp-surface schema [-h]
                           [--model {runspec,coordinate,schedule,objectives,all}]
                           [--output OUTPUT] [--format {json,yaml}]

options:
  -h, --help            show this help message and exit
  --model {runspec,coordinate,schedule,objectives,all}
                        Which schema to dump
  --output OUTPUT       Output file path (stdout if omitted)
  --format {json,yaml}  Output format
```

