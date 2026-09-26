"""Session-wide test environment, applied before anything imports torch.

The reduction pin used to live here as `OMP_NUM_THREADS=1`, and before that
in `tests/conftest.py` below its own `import torch`, where it did nothing:
OpenMP reads the variable once, at import. What the pin buys is measured,
not assumed (`scripts/probes/todo35_d16_determinism.py`): a seeded CPU demo
arm is bit-identical across processes at a fixed thread count, and differs
by ~1e-4 in accuracy between 1 and 8 threads.

It is not set here any more. Pinning the environment for the whole suite
costs 96s -> 186s in the fast lane, and only the demos' *records* need a
fixed reduction order. `tests/integration/conftest.py` pins the thread count
for the tier that emits them, and every record names the count it was
reduced under.
"""
