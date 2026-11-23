"""
Neuromorphic Domain Tasks

Spiking neuromorphic datasets (spiking MNIST, DVS Gestures, etc.)
"""

import numpy as np
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
    "SpikingMNISTTask",
    "DVSGesturesTask",
]


class SpikingMNISTTask(DomainTask):
    """MNIST frames as binary spike rasters for a neuromorphic substrate.

    A pixel carries a spike when its intensity clears a fixed rate threshold.
    The frame stays flat ``(784,)``, so a layer geometry reads the rate code
    directly while the substrate owns the event semantics; the threshold is the
    rate code's one knob, and it changes the spike density, not the dataset.
    """

    def __init__(
        self,
        name: str = "spiking_mnist",
        data_dir: str = "./data",
        download: bool = True,
        num_workers: int = 0,
        rate: float = 0.5,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.data_dir = data_dir
        self.download = download
        self.num_workers = num_workers
        self.rate = rate

    @property
    def domain_type(self) -> DomainType:
        return DomainType.NEUROMORPHIC

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.NEUROMORPHIC,
            description="Spiking MNIST: MNIST frames as binary spike rasters",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["classification"],
            default_batch_size=64,
            default_lr=1e-3,
            requires_spatial=True,
            tags=["neuromorphic", "spiking", "mnist"],
        )

    def setup(self) -> None:
        def frames(dataset) -> TensorDataset:
            spikes = (dataset.data.float() / 255.0 > self.rate).float()
            return TensorDataset(spikes.view(len(dataset), -1), dataset.targets)

        train_ds = frames(
            datasets.MNIST(self.data_dir, train=True, download=self.download)
        )
        val_ds = frames(
            datasets.MNIST(self.data_dir, train=False, download=self.download)
        )
        batch_size = 32 if self.quick_mode else 64
        self._train_loader = DataLoader(
            train_ds, batch_size=batch_size, shuffle=True, num_workers=self.num_workers
        )
        self._val_loader = DataLoader(
            val_ds, batch_size=batch_size, shuffle=False, num_workers=self.num_workers
        )
        self._test_loader = self._val_loader
        self._input_dim = 784
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


class DVSGesturesTask(DomainTask):
    """DVS Gestures: event-based gesture recognition from dynamic vision sensor.

    The DVS Gestures dataset contains recordings of 11 hand gestures from
    a Dynamic Vision Sensor (DVS). Events are accumulated into frames for
    compatibility with standard layer geometries.
    """

    def __init__(
        self,
        name: str = "dvs_gestures",
        data_dir: str = "./data",
        download: bool = True,
        num_workers: int = 0,
        time_bins: int = 20,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.data_dir = data_dir
        self.download = download
        self.num_workers = num_workers
        self.time_bins = time_bins

    @property
    def domain_type(self) -> DomainType:
        return DomainType.NEUROMORPHIC

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.NEUROMORPHIC,
            description="DVS Gestures: event-based gesture recognition",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["classification"],
            default_batch_size=32,
            default_lr=1e-3,
            requires_spatial=True,
            tags=["neuromorphic", "dvs", "event", "gesture"],
        )

    def setup(self) -> None:
        # DVS Gestures is not in torchvision; use synthetic fallback for quick_mode
        # In production, this would download from the original source
        if self.quick_mode:
            # Synthetic data: 11 classes, 128x128 spatial, time_bins temporal
            num_train = 1000
            num_val = 200
            c, h, w = 2, 128, 128  # DVS has 2 polarity channels
            train_x = torch.randn(num_train, self.time_bins, c, h, w)
            train_y = torch.randint(0, 11, (num_train,))
            val_x = torch.randn(num_val, self.time_bins, c, h, w)
            val_y = torch.randint(0, 11, (num_val,))

            # Flatten spatial dimensions for layer geometries
            train_x = train_x.view(num_train, self.time_bins, -1)
            val_x = val_x.view(num_val, self.time_bins, -1)
        else:
            # TODO: implement real DVS Gestures loader
            raise NotImplementedError(
                "Real DVS Gestures loader not implemented; use quick_mode=True"
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
        self._input_dim = (self.time_bins, 2, 128, 128)  # (T, C, H, W)
        self._output_dim = 11
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