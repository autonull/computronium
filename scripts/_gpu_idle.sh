#!/usr/bin/env bash
# A CUDA context that already holds device memory when a suite starts is
# foreign: a killed run's worker, or another user's. It costs memory a
# memory-binding test then measures as a neighbour's, and a 9.66 GiB device
# overflows sooner (measured: a killed run's leftover held 1046 MiB and the
# next affected tier failed nine tests with CUDA OOM).
#
# This warns; it does not kill. The owner of the process is the one who can.
warn_foreign_gpu_allocations() {
    if ! command -v nvidia-smi >/dev/null 2>&1; then
        return 0
    fi
    local foreign
    foreign=$(nvidia-smi --query-compute-apps=pid,used_memory \
        --format=csv,noheader 2>/dev/null || true)
    if [ -n "$foreign" ]; then
        printf 'warning: the GPU holds allocations before this run:\n%s\n' \
            "$foreign" >&2
    fi
}
