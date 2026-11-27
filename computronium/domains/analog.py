"""
Analog Domain Tasks

Analog/memristive simulation tasks (memristor crossbar simulation, etc.)
"""

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

from computronium.domains.base import (
    DomainSpec,
    DomainTask,
    DomainType,
    Metrics,
    TaskSplit,
)

__all__ = [
    "MemristorSimulationTask",
]


class MemristorSimulationTask(DomainTask):
    """Memristor crossbar simulation: MNIST with simulated memristor non-idealities.

    This simulates the effects of memristor crossbar arrays (stuck-at faults,
    conductance variability, non-linearity, sneak paths) on neural network
    inference and training.
    """

    def __init__(
        self,
        name: str = "memristor_simulation",
        data_dir: str = "./data",
        download: bool = True,
        num_workers: int = 0,
        stuck_at_fault_rate: float = 0.01,
        conductance_variability: float = 0.05,
        non_linearity: float = 0.1,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.data_dir = data_dir
        self.download = download
        self.num_workers = num_workers
        self.stuck_at_fault_rate = stuck_at_fault_rate
        self.conductance_variability = conductance_variability
        self.non_linearity = non_linearity

    @property
    def domain_type(self) -> DomainType:
        return DomainType.ANALOG

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.ANALOG,
            description="Memristor simulation: MNIST with memristor crossbar non-idealities",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["classification"],
            default_batch_size=64,
            default_lr=1e-3,
            requires_spatial=True,
            tags=["analog", "memristor", "crossbar", "mnist", "simulation"],
        )

    def setup(self) -> None:
        def apply_memristor_effects(images: torch.Tensor) -> torch.Tensor:
            """Apply simulated memristor crossbar effects."""
            # images: [B, 1, 28, 28] normalized to [0, 1]
            # Simulate conductance variability
            noise = torch.randn_like(images) * self.conductance_variability
            images = (images + noise).clamp(0, 1)

            # Simulate stuck-at faults (random pixels stuck at 0 or 1)
            if self.stuck_at_fault_rate > 0:
                fault_mask = torch.rand_like(images) < self.stuck_at_fault_rate
                stuck_values = torch.randint(0, 2, images.shape, dtype=images.dtype)
                images = torch.where(fault_mask, stuck_values.float(), images)

            # Simulate non-linear I-V characteristic
            if self.non_linearity > 0:
                images = torch.sigmoid(
                    torch.logit(images.clamp(1e-6, 1 - 1e-6)) * (1 + self.non_linearity)
                )

            return images

        transform = None
        train_ds = datasets.MNIST(
            self.data_dir, train=True, download=self.download, transform=transform
        )
        val_ds = datasets.MNIST(
            self.data_dir, train=False, download=self.download, transform=transform
        )

        train_x = train_ds.data.float() / 255.0
        train_x = train_x.unsqueeze(1)  # [B, 1, 28, 28]
        train_x = apply_memristor_effects(train_x)
        train_y = train_ds.targets

        val_x = val_ds.data.float() / 255.0
        val_x = val_x.unsqueeze(1)
        val_x = apply_memristor_effects(val_x)
        val_y = val_ds.targets

        train_ds = TensorDataset(train_x, train_y)
        val_ds = TensorDataset(val_x, val_y)
        batch_size = 32 if self.quick_mode else 64
        self._train_loader = DataLoader(
            train_ds, batch_size=batch_size, shuffle=True, num_workers=self.num_workers
        )
        self._val_loader = DataLoader(
            val_ds, batch_size=batch_size, shuffle=False, num_workers=self.num_workers
        )
        self._test_loader = self._val_loader
        self._input_dim = (1, 28, 28)
        self._output_dim = 10
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
            with torch.no_grad():
                for i, (inputs, targets) in enumerate(loader):
                    if max_batches and i >= max_batches:
                        break
                    inputs, targets = inputs.to(self.device), targets.to(self.device)
                    outputs = model(inputs)
                    loss = self.compute_loss(outputs, targets)
                    total_loss += loss.item() * inputs.size(0)
                    total_correct += (outputs.argmax(1) == targets).sum().item()
                    total_samples += inputs.size(0)
            avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
            accuracy = total_correct / total_samples if total_samples > 0 else 0.0
        finally:
            if was_training:
                model.train()
        return Metrics(loss=avg_loss, accuracy=accuracy)
