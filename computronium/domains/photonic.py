"""
Photonic Domain Tasks

Optical/photonic simulation tasks (optical MNIST simulation, etc.)
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
    "OpticalMNISTSimTask",
]


class OpticalMNISTSimTask(DomainTask):
    """Optical MNIST simulation: MNIST with simulated optical noise and diffraction.

    This simulates the effects of optical propagation (diffraction, noise,
    crosstalk) on MNIST images, as would be encountered in photonic neural
    network implementations.
    """

    def __init__(
        self,
        name: str = "optical_mnist_sim",
        data_dir: str = "./data",
        download: bool = True,
        num_workers: int = 0,
        noise_std: float = 0.1,
        diffraction_kernel_size: int = 3,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.data_dir = data_dir
        self.download = download
        self.num_workers = num_workers
        self.noise_std = noise_std
        self.diffraction_kernel_size = diffraction_kernel_size

    @property
    def domain_type(self) -> DomainType:
        return DomainType.PHOTONIC

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.PHOTONIC,
            description="Optical MNIST: MNIST with simulated optical noise and diffraction",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["classification"],
            default_batch_size=64,
            default_lr=1e-3,
            requires_spatial=True,
            tags=["photonic", "optical", "mnist", "simulation"],
        )

    def setup(self) -> None:
        def apply_optical_effects(images: torch.Tensor) -> torch.Tensor:
            """Apply simulated optical effects: diffraction blur + noise."""
            # Simple diffraction blur via average pooling
            from torch.nn.functional import avg_pool2d

            # images: [B, 1, 28, 28]
            blurred = avg_pool2d(
                images,
                kernel_size=self.diffraction_kernel_size,
                stride=1,
                padding=self.diffraction_kernel_size // 2,
            )
            # Add optical noise (shot noise + thermal noise)
            noise = torch.randn_like(blurred) * self.noise_std
            return (blurred + noise).clamp(0, 1)

        transform = None
        train_ds = datasets.MNIST(
            self.data_dir, train=True, download=self.download, transform=transform
        )
        val_ds = datasets.MNIST(
            self.data_dir, train=False, download=self.download, transform=transform
        )

        train_x = train_ds.data.float() / 255.0
        train_x = train_x.unsqueeze(1)  # [B, 1, 28, 28]
        train_x = apply_optical_effects(train_x)
        train_y = train_ds.targets

        val_x = val_ds.data.float() / 255.0
        val_x = val_x.unsqueeze(1)
        val_x = apply_optical_effects(val_x)
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