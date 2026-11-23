"""
Quantum Domain Tasks

Quantum simulation tasks (quantum circuit learning, etc.)
"""

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from computronium.domains.base import (
    DomainSpec,
    DomainTask,
    DomainType,
    Metrics,
    TaskSplit,
)

__all__ = [
    "QuantumCircuitLearningTask",
]


class QuantumCircuitLearningTask(DomainTask):
    """Quantum circuit learning: learn parameters of a parameterized quantum circuit.

    The task is to learn the parameters of a variational quantum circuit to
    prepare a target state or minimize a cost function (e.g., VQE for
    ground state energy). This is simulated classically for quick_mode.
    """

    def __init__(
        self,
        name: str = "quantum_circuit_learning",
        num_qubits: int = 4,
        num_layers: int = 3,
        target_state: str = "ghz",
        shots: int = 1024,
        num_workers: int = 0,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.target_state = target_state
        self.shots = shots
        self.num_workers = num_workers

    @property
    def domain_type(self) -> DomainType:
        return DomainType.QUANTUM

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.QUANTUM,
            description=f"Quantum circuit learning: {self.target_state} state prep",
            default_metrics=["fidelity", "loss"],
            supported_tasks=["optimization", "state_preparation"],
            default_batch_size=32,
            default_lr=1e-2,
            tags=["quantum", "vqe", "variational", "circuit"],
        )

    def setup(self) -> None:
        # For quick_mode, use a classical surrogate: random features mapped to
        # fidelity-like objective. Real implementation would use a quantum simulator.
        if self.quick_mode:
            # Synthetic data: parameter vectors -> fidelity
            num_params = self.num_qubits * self.num_layers * 3  # 3 rotations per qubit per layer
            num_train = 500
            num_val = 100

            # Generate random parameter vectors
            train_x = torch.randn(num_train, num_params)
            # Target: fidelity with target state (simulated as smooth function of params)
            # For GHZ state, fidelity is high when params are near specific values
            target_params = torch.zeros(num_params)
            train_fidelity = torch.exp(-0.5 * ((train_x - target_params) ** 2).sum(dim=1))
            train_y = (train_fidelity > 0.5).long()  # Binary: high fidelity vs low

            val_x = torch.randn(num_val, num_params)
            val_fidelity = torch.exp(-0.5 * ((val_x - target_params) ** 2).sum(dim=1))
            val_y = (val_fidelity > 0.5).long()
        else:
            # TODO: implement real quantum circuit simulation (PennyLane, Qiskit, etc.)
            raise NotImplementedError(
                "Real quantum circuit simulation not implemented; use quick_mode=True"
            )

        train_ds = TensorDataset(train_x, train_y)
        val_ds = TensorDataset(val_x, val_y)
        batch_size = 16 if self.quick_mode else 32
        self._train_loader = DataLoader(
            train_ds, batch_size=batch_size, shuffle=True, num_workers=self.num_workers
        )
        self._val_loader = DataLoader(
            val_ds, batch_size=batch_size, shuffle=False, num_workers=self.num_workers
        )
        self._test_loader = self._val_loader
        self._input_dim = num_params
        self._output_dim = 2  # Binary classification: high/low fidelity
        self._setup_done = True

    def get_dataloader(self, split: TaskSplit) -> DataLoader:
        if not self._setup_done:
            self.setup()
        if split == TaskSplit.TRAIN:
            return self._train_loader
        return self._val_loader

    def evaluate(
        self,
        model: nn.Module,
        split: TaskSplit = TaskSplit.VAL,
        max_batches: int | None = None,
    ) -> Metrics:
        was_training = model.training
        model.eval()
        try:
            loader = self.get_dataloader(split)
            total_loss = 0.0
            total_correct = 0
            total_samples = 0
            total_fidelity = 0.0
            with torch.no_grad():
                for i, (x, y) in enumerate(loader):
                    if max_batches is not None and i >= max_batches:
                        break
                    x = x.to(self.device)
                    y = y.to(self.device)
                    logits = model(x)
                    loss = nn.functional.cross_entropy(logits, y)
                    total_loss += loss.item() * x.size(0)
                    pred = logits.argmax(dim=1)
                    total_correct += (pred == y).sum().item()
                    total_samples += x.size(0)
                    # Compute fidelity metric
                    probs = torch.softmax(logits, dim=1)
                    total_fidelity += probs[:, 1].sum().item()
            avg_loss = total_loss / total_samples if total_samples > 0 else float("inf")
            accuracy = total_correct / total_samples if total_samples > 0 else 0.0
            avg_fidelity = total_fidelity / total_samples if total_samples > 0 else 0.0
            return Metrics(
                loss=avg_loss,
                accuracy=accuracy,
                custom={"fidelity": avg_fidelity},
            )
        finally:
            if was_training:
                model.train()