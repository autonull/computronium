"""NtmGeometry behavior tests (TODO.ntm_nca.md §10/W8.5 promotion)."""

import pytest
import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

from computronium import (
    GeometryConfig,
    NtmGeometry,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemConfig,
)
from computronium.ontology.geometry import geometry_from_config
from computronium.ontology.utils.params import apply_pseudo_gradients

BATCH = 4
SEQ = 5


def _geometry(**kwargs) -> NtmGeometry:
    config = GeometryConfig.ntm(input_dim=1, output_dim=2, **kwargs)
    geometry = geometry_from_config(config)
    assert isinstance(geometry, NtmGeometry)
    return geometry


def _copy_inputs(bits: Tensor, width: int) -> Tensor:
    """(B, L) bits -> (B, 2L+1, 1) controller inputs (bit, blank, blank)."""
    inputs = torch.zeros(bits.size(0), 2 * bits.size(1) + 1, 1)
    inputs[:, : bits.size(1), 0] = bits.float()
    return inputs


class TestNtmStep:
    def test_slot_embeddings_are_distinct_and_retrievable(self) -> None:
        geometry = _geometry()
        mem = geometry.init_mem(BATCH)
        # each slot carries a UNIQUE identity vector (Q4 collision fix:
        # no two slots share an embedding, even when mem_slots > mem_width)
        for s in range(geometry.config.mem_slots):
            for t in range(s + 1, geometry.config.mem_slots):
                assert not torch.allclose(mem[0, s], mem[0, t])
        # exact one-hot identities when mem_slots <= mem_width
        wide = _geometry(mem_slots=8, mem_width=16)
        wmem = wide.init_mem(BATCH)
        eye = torch.eye(wide.config.mem_width)
        for s in range(wide.config.mem_slots):
            assert torch.allclose(wmem[0, s], eye[s] * 0.5)
        # retrievability: a key equal to a slot's embedding addresses it
        a_r = geometry._address(mem, mem[:, 3])
        assert a_r[0].argmax() == 3
        assert abs(a_r[0].sum().item() - 1.0) < 1e-5

    def test_write_then_read_round_trip(self) -> None:
        """§11.10 mechanics: retrievable (non-negative) content placed at a
        slot is recovered by the cosine addressing; the Q4 collision fix
        removes the tie-split (mass concentrates on the written slot)."""
        geometry = _geometry()
        mem = geometry.init_mem(BATCH)
        content = torch.zeros(BATCH, geometry.config.mem_width)
        content[:, 2] = 0.5 + 0.5  # bit=1 pattern on channel 2
        a_w = torch.zeros(BATCH, geometry.config.mem_slots)
        a_w[:, 2] = 1.0
        erase_v = torch.ones(BATCH, geometry.config.mem_width)
        mem_next = mem * (1 - a_w.unsqueeze(2) * erase_v.unsqueeze(1)) + (
            a_w.unsqueeze(2) * content.unsqueeze(1)
        )
        a_r = geometry._address(mem_next, content)
        read = torch.einsum("bs,bsw->bw", a_r, mem_next)
        assert a_r[0, 2] > 0.9
        assert read[0].argmax() == 2
        assert read[0, 2] > 0.4

    def test_step_shapes_and_addressing(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry()
        x = torch.randn(BATCH, geometry.config.input_dim)
        logits, read, mem_next, a_w, a_r, state = geometry.step(x)
        assert logits.shape == (BATCH, geometry.config.output_dim)
        assert read.shape == (BATCH, geometry.config.mem_width)
        assert mem_next.shape == (
            BATCH,
            geometry.config.mem_slots,
            geometry.config.mem_width,
        )
        assert a_w.shape == a_r.shape == (BATCH, geometry.config.mem_slots)
        assert a_w.sum(-1).allclose(torch.ones(BATCH), atol=1e-5)
        assert state[0].shape[1] == BATCH

    def test_episode_matches_step_loop(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry()
        bits = torch.randint(0, 2, (BATCH, SEQ))
        inputs = _copy_inputs(bits, geometry.config.mem_width)
        logits, _mem = geometry.episode(inputs)
        manual = []
        state = mem = read = None
        for t in range(inputs.shape[1]):
            l_t, read, mem, _aw, _ar, state = geometry.step(
                inputs[:, t], state, mem, read
            )
            manual.append(l_t)
        assert torch.allclose(logits, torch.stack(manual, dim=1))

    def test_update_params_round_trip(self) -> None:
        torch.manual_seed(0)
        geometry = _geometry()
        clone = _geometry()
        clone.update_params(geometry.params)
        for name, tensor in geometry.params.items():
            assert torch.equal(clone.params[name], tensor)

    def test_invalid_input_shape_raises(self) -> None:
        geometry = _geometry()
        with pytest.raises(ValueError, match="NtmGeometry expects x"):
            geometry.step(torch.randn(BATCH, 3))


class TestNtmCreditUpdateComposition:
    def test_pseudo_gradient_update_moves_weights(self) -> None:
        """The real composition path: zero-history local loss on the
        geometry's own parameters -> apply_pseudo_gradients -> weights move."""
        torch.manual_seed(0)
        geometry = _geometry()
        before = {n: t.detach().clone() for n, t in geometry.params.items()}
        bits = torch.randint(0, 2, (BATCH, SEQ))
        inputs = _copy_inputs(bits, geometry.config.mem_width)
        targets = torch.zeros(BATCH, inputs.shape[1], dtype=torch.long)
        targets[:, SEQ + 1 :] = bits
        for _ in range(2):
            logits, _mem = geometry.episode(inputs, grad=True)
            loss = F.cross_entropy(logits.reshape(-1, 2), targets.reshape(-1))
            grads = torch.autograd.grad(
                loss, list(geometry.params.values()), allow_unused=True
            )
            weight_grads = [
                g
                for n, g in zip(geometry.params, grads, strict=True)
                if "weight" in n and g is not None
            ]
            assert weight_grads and any(g.abs().sum() > 0 for g in weight_grads)
            bias_grads = {
                n: g
                for n, g in zip(geometry.params, grads, strict=True)
                if "bias" in n and g is not None
            }
            new = apply_pseudo_gradients(
                geometry.params,
                weight_grads,
                lambda _n, p_, g: p_ - 0.05 * g,
                bias_grads,
            )
            geometry.update_params(new)
        assert any(
            not torch.equal(geometry.params[n], before[n])
            for n in geometry.params
            if "weight" in n
        )

    def test_system_config_rejects_non_instantaneous_dynamics(self) -> None:
        from computronium import CreditAssignmentConfig

        config = SystemConfig(
            substrate=SubstrateConfig.digital(),
            geometry=GeometryConfig.ntm(input_dim=1, output_dim=2),
            dynamics=StateDynamicsConfig.energy_minimization(),
            credit=CreditAssignmentConfig.gradient(),
            update=ParameterUpdateConfig.euclidean(),
        )
        with pytest.raises(ValueError, match="NTM geometry requires instantaneous"):
            config.validate()


class TestNtmCopyLearnability:
    @staticmethod
    def _copy_acc(geometry: NtmGeometry, seq: int, seed: int = 999) -> float:
        """Greedy copy accuracy on a fresh draw (0.5 = all-bit chance)."""
        bits = torch.randint(
            0, 2, (16, seq), generator=torch.Generator().manual_seed(seed)
        )
        with torch.no_grad():
            logits, _mem = geometry.episode(
                _copy_inputs(bits, geometry.config.mem_width)
            )
        targets = torch.zeros(16, 2 * seq + 1, dtype=torch.long)
        targets[:, seq + 1 :] = bits
        mask = targets != -100
        return float(
            ((logits.argmax(-1) == targets) & mask).float().sum() / mask.float().sum()
        )

    def test_bptt_learns_copy_mechanics(self) -> None:
        """The §20 gate at promotion scale: short-BPTT on L=4 copy descends
        materially and beats the 0.5 all-bit chance on a fresh draw."""
        geometry = _geometry()
        opt = torch.optim.Adam(geometry.parameters(), lr=1e-3)
        gen = torch.Generator().manual_seed(7)
        seq = 4
        first_loss = 0.0
        for step in range(1200):
            bits = torch.randint(0, 2, (16, seq), generator=gen)
            inputs = _copy_inputs(bits, geometry.config.mem_width)
            logits, _mem = geometry.episode(inputs, grad=True)
            targets = torch.zeros(16, 2 * seq + 1, dtype=torch.long)
            targets[:, seq + 1 :] = bits
            loss = F.cross_entropy(logits.reshape(-1, 2), targets.reshape(-1))
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(geometry.parameters(), 5.0)
            opt.step()
            if step == 0:
                first_loss = float(loss.detach())
        acc = self._copy_acc(geometry, seq)
        assert acc > 0.6, (
            f"copy acc {acc:.3f} after 1200 steps (first loss {first_loss:.3f})"
        )
