# Computronium Experiment Loop

- cycles: 1
- tasks: xor, iris, spiral, digits, breast_cancer, wine, cartpole, copy_task
- objective set: param_count, validation_accuracy, validation_loss, walltime_total

| cycle | task | kind | records | pass | L1 | L2 | baseline |
|------:|------|------|--------:|-----:|---:|---:|----------|
| 0 | xor | explore | 20 | 18 | 18 | 0 | yes |

## Gate Calibration

- L0→L1 promotion rate: 90.0% (18/20)
- L1→L2 promotion rate: 0.0% (0/18)
- Threshold guidance: >90% ⇒ too loose; <5% ⇒ too strict

## Metric Gaps (Unmeasured Objectives)

- cartpole: mean_reward, std_reward

## Limitations

- Coverage is the cheap multi-domain set; language and graph tasks are not yet in the fast path.
- The frontier is comparable within-task only until every task has an online baseline (TODO63 Phase 2).
