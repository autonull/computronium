# Disabled GitHub Actions

GitHub runs only YAML files in `.github/workflows/`. This directory is
outside that path on purpose: the repository is not using GitHub Actions.

To re-enable a workflow, move its file back to `.github/workflows/` and
re-run `scripts/run_local_gates.sh` as the local gate first.
