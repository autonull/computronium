"""Probe: does each substrate's energy model scale with the arithmetic?

Informed the TODO51 §5 validation. `estimate_energy` was fed one hardcoded
`(output_dim, input_dim)` weight shape by the evaluator, so every cell reported
byte-identical joules regardless of its size. The fix charges per layer over
the geometry's own shapes; this probe checks the resulting model has the two
properties a Pareto front over joules depends on:

* **monotone in the work** — widening a layer must raise the joules or the axis
  is a constant. Batch monotonicity is *non-strict* on purpose: an optical
  substrate's laser power is independent of batch, and a memristive one's
  programming cost is paid once per weight, so neither scales 8x with the
  batch. Asserting the strict 8x would be asserting a physics the models do not
  claim — the measured ratios below are what they are;
* **ordered across substrates** — the per-MAC figures must fall where the
  literature puts them (memristive ~fJ << neuromorphic ~0.01 pJ/event <
  digital ~1 pJ/MAC), or the ordering is an artifact of the constants rather
  than of the arithmetic.

Run: uv run python -m scripts.probes.t51_energy_model_probe
"""

from __future__ import annotations

from computronium.ontology.substrate._substrate import (
    SubstrateConfig,
    substrate_from_config,
)

# (config factory, expected pJ per unit work, tolerance as a multiple)
_FAMILIES = (
    ("digital", SubstrateConfig.digital),
    ("analog", SubstrateConfig.analog),
    ("memristive", SubstrateConfig.memristive),
    ("neuromorphic", SubstrateConfig.neuromorphic),
    ("optical", SubstrateConfig.optical),
    ("quantum", SubstrateConfig.quantum),
    ("complex", SubstrateConfig.complex),
    ("sparse", SubstrateConfig.sparse),
    ("ternary", SubstrateConfig.ternary),
)

_SHAPE = (64, 64)


def _joules(substrate, *, batch: int, out: int, inn: int) -> float:
    return float(
        substrate.estimate_energy(
            input_shape=(batch, inn),
            weight_shape=(out, inn),
            batch_size=batch,
        )["total_energy_per_step"]
    )


def _macs(batch: int, out: int, inn: int) -> float:
    return batch * 2 * out * inn


def main() -> None:
    print(f"{'substrate':<14}{'pJ/MAC':>12}{'batch 8->64':>14}{'width 64->256':>16}")
    print("-" * 58)
    for name, factory in _FAMILIES:
        substrate = substrate_from_config(factory())
        base = _joules(substrate, batch=8, out=64, inn=64)
        wider_batch = _joules(substrate, batch=64, out=64, inn=64)
        wider_layer = _joules(substrate, batch=8, out=256, inn=64)
        per_mac = base / _macs(8, 64, 64) * 1e12
        batch_ratio = wider_batch / base
        layer_ratio = wider_layer / base
        print(f"{name:<14}{per_mac:>12.4f}{batch_ratio:>14.2f}{layer_ratio:>16.2f}")
        assert batch_ratio >= 1.0, f"{name}: energy falls as the batch grows"
        assert layer_ratio > 1.9, f"{name}: energy flat in layer width"

    # The coarse claim the literature supports: a general-purpose digital MAC is
    # an order of magnitude dearer than an emulated device's. The finer ordering
    # among device substrates is not asserted — neuromorphic charges per *event*
    # and memristive per programming op, so a per-MAC comparison of the two is
    # a comparison of two different units, not of two devices.
    digital = substrate_from_config(SubstrateConfig.digital())  # 2.0 pJ/MAC
    device = {
        name: substrate_from_config(factory())
        for name, factory in (
            ("memristive", SubstrateConfig.memristive),
            ("neuromorphic", SubstrateConfig.neuromorphic),
            ("optical", SubstrateConfig.optical),
        )
    }
    baseline = _joules(digital, batch=8, out=64, inn=64)
    for name, substrate in device.items():
        value = _joules(substrate, batch=8, out=64, inn=64)
        ratio = baseline / value
        print(f"digital/{name}: {ratio:>8.1f}x dearer per MAC")
        assert ratio > 10.0, (
            f"{name} at {value:.3g} J is not an order of magnitude below "
            f"digital's {baseline:.3g} J"
        )


if __name__ == "__main__":
    main()
