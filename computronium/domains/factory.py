"""
Task factory for the merged task hierarchy.

All concrete task classes now live in ``domains/``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import nn

if TYPE_CHECKING:
    from torch.utils.data import DataLoader

from computronium.core.logging import get_logger
from computronium.domains.base import (
    DomainSpec,
    DomainTask,
    DomainType,
    Metrics,
    TaskSplit,
)
from computronium.domains.timeseries import TimeSeriesTask
from computronium.domains.trainer import _TaskTrainer

__all__ = [
    "CharNGramTask",
    "CopyTask",
    "GraphClassificationTask",
    "SequentialMNISTTask",
    "TimeSeriesTask",
    "create_task",
    "logger",
]

logger = get_logger()


class SequentialMNISTTask(DomainTask):
    """Sequential MNIST: MNIST pixels fed as a sequence (1x784).

    This exercises recurrent, causal_transformer, NTM, and NCA geometries
    which require sequential input processing.
    """

    def __init__(
        self,
        name: str = "sequential_mnist",
        device: str = "cpu",
        quick_mode: bool = False,
        data_dir: str = "./data",
        download: bool = True,
        num_workers: int = 0,
        **kwargs,
    ):
        super().__init__(name, device=device, quick_mode=quick_mode, **kwargs)
        self.data_dir = data_dir
        self.download = download
        self.num_workers = num_workers
        self._input_dim = 784  # 28*28 flattened sequence
        self._output_dim = 10

    @property
    def domain_type(self) -> DomainType:
        return DomainType.VISION

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.VISION,
            description="Sequential MNIST: pixels fed as 784-step sequence",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["classification"],
            default_batch_size=64,
            default_lr=1e-3,
            requires_sequence=True,
            tags=["vision", "sequential", "mnist"],
        )

    def setup(self) -> None:
        from torch.utils.data import DataLoader, TensorDataset
        from torchvision import datasets

        transform = None  # We'll flatten manually
        train_ds = datasets.MNIST(
            self.data_dir,
            train=True,
            download=self.download,
            transform=transform,
        )
        val_ds = datasets.MNIST(
            self.data_dir,
            train=False,
            download=self.download,
            transform=transform,
        )

        # Flatten images to sequences: [B, 1, 28, 28] -> [B, 784]
        train_x = train_ds.data.float() / 255.0
        train_x = train_x.view(train_x.size(0), -1)  # [B, 784]
        train_y = train_ds.targets

        val_x = val_ds.data.float() / 255.0
        val_x = val_x.view(val_x.size(0), -1)
        val_y = val_ds.targets

        train_ds = TensorDataset(train_x, train_y)
        val_ds = TensorDataset(val_x, val_y)

        self._train_loader = DataLoader(
            train_ds,
            batch_size=32 if self.quick_mode else 64,
            shuffle=True,
            num_workers=self.num_workers,
        )
        self._val_loader = DataLoader(
            val_ds,
            batch_size=32 if self.quick_mode else 64,
            shuffle=False,
            num_workers=self.num_workers,
        )
        self._test_loader = self._val_loader
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
                for i, (batch_inputs, batch_targets) in enumerate(loader):
                    if max_batches and i >= max_batches:
                        break
                    dev_inputs = batch_inputs.to(self.device)
                    dev_targets = batch_targets.to(self.device)
                    outputs = model(dev_inputs)
                    loss = self.compute_loss(outputs, dev_targets)
                    total_loss += loss.item() * dev_inputs.size(0)
                    total_correct += (outputs.argmax(1) == dev_targets).sum().item()
                    total_samples += dev_inputs.size(0)
            avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
            accuracy = total_correct / total_samples if total_samples > 0 else 0.0
        finally:
            if was_training:
                model.train()
        return Metrics(loss=avg_loss, accuracy=accuracy)


class CopyTask(DomainTask):
    """Copy task: Model must predict the next token in a sequence after a delimiter.

    This exercises attention, recurrent, and NTM geometries which require
    memory and sequence processing. The task is framed as next-token prediction:
    given the input sequence + delimiter + prefix of copied sequence, predict
    the next token in the copied sequence.
    """

    def __init__(
        self,
        name: str = "copy_task",
        device: str = "cpu",
        quick_mode: bool = False,
        seq_len: int = 10,
        vocab_size: int = 8,
        num_workers: int = 0,
        **kwargs,
    ):
        super().__init__(name, device=device, quick_mode=quick_mode, **kwargs)
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.num_workers = num_workers
        # Input: padded to max_len = 2*seq_len + 1 (original seq + delimiter + max copied prefix)
        # Output: vocab_size (next token prediction)
        self._input_dim = 2 * seq_len + 1
        self._output_dim = vocab_size

    @property
    def domain_type(self) -> DomainType:
        return DomainType.TIMESERIES

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.TIMESERIES,
            description="Copy task: next-token prediction after delimiter",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["sequence_copy"],
            default_batch_size=64,
            default_lr=1e-3,
            requires_sequence=True,
            tags=["timeseries", "memory", "copy"],
        )

    def setup(self) -> None:
        import torch
        from torch.utils.data import DataLoader, TensorDataset

        # Generate synthetic copy task data
        n_train = 1000 if self.quick_mode else 10000
        n_val = 200 if self.quick_mode else 2000

        # Input sequences: random tokens from vocab
        train_seq = torch.randint(0, self.vocab_size, (n_train, self.seq_len))
        val_seq = torch.randint(0, self.vocab_size, (n_val, self.seq_len))

        # Delimiter token (vocab_size)
        delimiter = torch.full((n_train, 1), self.vocab_size, dtype=torch.long)
        val_delimiter = torch.full((n_val, 1), self.vocab_size, dtype=torch.long)

        # Create next-token prediction samples
        # For each sequence, create samples: (prefix + delimiter + copied_prefix) -> next_token
        # We'll generate all positions in the copy phase
        def create_samples(seqs, delims):
            samples_x = []
            samples_y = []
            for seq, delim in zip(seqs, delims):
                # Input: original sequence + delimiter
                context = torch.cat([seq, delim])  # [seq_len + 1]
                # Targets: the sequence itself (copy phase)
                for t in range(self.seq_len):
                    # Input at step t: context + copied prefix up to t
                    prefix = seq[:t] if t > 0 else torch.empty(0, dtype=torch.long)
                    x = torch.cat([context, prefix])  # [seq_len + 1 + t]
                    y = seq[t]  # next token to predict
                    samples_x.append(x)
                    samples_y.append(y)
            return torch.nested.nested_tensor(samples_x), torch.stack(samples_y)

        # For simplicity, use fixed-length input by padding
        # Max input length: seq_len (original) + 1 (delimiter) + seq_len (max copied prefix) = 2*seq_len + 1
        max_len = 2 * self.seq_len + 1
        pad_token = self.vocab_size + 1  # Use a different token for padding

        def create_padded_samples(seqs, delims):
            samples_x = []
            samples_y = []
            for seq, delim in zip(seqs, delims):
                context = torch.cat([seq, delim])  # [seq_len + 1]
                for t in range(self.seq_len):
                    prefix = seq[:t] if t > 0 else torch.empty(0, dtype=torch.long)
                    x = torch.cat([context, prefix])  # [seq_len + 1 + t]
                    # Pad to max_len
                    if len(x) < max_len:
                        x = torch.cat([
                            x,
                            torch.full(
                                (max_len - len(x),), pad_token, dtype=torch.long
                            ),
                        ])
                    samples_x.append(x)
                    samples_y.append(seq[t])
            return torch.stack(samples_x).float(), torch.stack(samples_y)

        train_x, train_y = create_padded_samples(train_seq, delimiter)
        val_x, val_y = create_padded_samples(val_seq, val_delimiter)

        train_ds = TensorDataset(train_x, train_y)
        val_ds = TensorDataset(val_x, val_y)

        self._train_loader = DataLoader(
            train_ds,
            batch_size=32 if self.quick_mode else 64,
            shuffle=True,
            num_workers=self.num_workers,
        )
        self._val_loader = DataLoader(
            val_ds,
            batch_size=32 if self.quick_mode else 64,
            shuffle=False,
            num_workers=self.num_workers,
        )
        self._test_loader = self._val_loader
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
                for i, (batch_inputs, batch_targets) in enumerate(loader):
                    if max_batches and i >= max_batches:
                        break
                    dev_inputs = batch_inputs.to(self.device)
                    dev_targets = batch_targets.to(self.device)
                    outputs = model(dev_inputs)
                    loss = self.compute_loss(outputs, dev_targets)
                    total_loss += loss.item() * dev_inputs.size(0)
                    total_correct += (outputs.argmax(1) == dev_targets).sum().item()
                    total_samples += dev_inputs.size(0)
            avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
            accuracy = total_correct / total_samples if total_samples > 0 else 0.0
        finally:
            if was_training:
                model.train()
        return Metrics(loss=avg_loss, accuracy=accuracy)

    def compute_loss(
        self, outputs: torch.Tensor, targets: torch.Tensor
    ) -> torch.Tensor:
        # Handle padded inputs: mask out padding tokens in loss
        # For now, use standard cross_entropy (padding tokens will have random targets)
        # A proper implementation would mask the loss
        return torch.nn.functional.cross_entropy(outputs, targets)


class GraphClassificationTask(DomainTask):
    """Graph classification: Classify entire graphs (not nodes).

    This exercises graph and spatial_lattice geometries.
    Uses TUDataset (e.g., MUTAG, PROTEINS, ENZYMES).
    """

    def __init__(
        self,
        name: str = "graph_classification",
        device: str = "cpu",
        quick_mode: bool = False,
        dataset_name: str = "MUTAG",
        num_workers: int = 0,
        **kwargs,
    ):
        super().__init__(name, device=device, quick_mode=quick_mode, **kwargs)
        self.dataset_name = dataset_name
        self.num_workers = num_workers
        self._input_dim = None  # Will be set in setup
        self._output_dim = None

    @property
    def domain_type(self) -> DomainType:
        return DomainType.GRAPH

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.GRAPH,
            description="Graph classification: classify entire graphs",
            default_metrics=["accuracy", "loss"],
            supported_tasks=["graph_classification"],
            default_batch_size=32,
            default_lr=1e-2,
            tags=["graph", "classification", "tu"],
        )

    def setup(self) -> None:
        try:
            from torch_geometric.datasets import TUDataset
            from torch_geometric.loader import DataLoader as GeoDataLoader
        except ImportError:
            raise ImportError(
                "torch-geometric required for graph classification. "
                "Install with: pip install torch-geometric"
            )

        dataset = TUDataset(root="./data", name=self.dataset_name)
        self._input_dim = dataset.num_features
        self._output_dim = dataset.num_classes

        # Split dataset
        n = len(dataset)
        n_train = int(0.8 * n)
        indices = torch.randperm(n)
        train_idx, val_idx = indices[:n_train], indices[n_train:]

        train_ds = dataset[train_idx]
        val_ds = dataset[val_idx]

        self._train_loader = GeoDataLoader(
            train_ds,
            batch_size=32 if self.quick_mode else 64,
            shuffle=True,
            num_workers=self.num_workers,
        )
        self._val_loader = GeoDataLoader(
            val_ds,
            batch_size=32 if self.quick_mode else 64,
            shuffle=False,
            num_workers=self.num_workers,
        )
        self._test_loader = self._val_loader
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
            # For graph classification, we need to handle batch differently
            loader = self.get_dataloader(split)
            total_loss = 0.0
            total_correct = 0
            total_samples = 0
            with torch.no_grad():
                for i, data_batch in enumerate(loader):
                    if max_batches and i >= max_batches:
                        break
                    dev_batch = data_batch.to(self.device)
                    outputs = model(dev_batch.x, dev_batch.edge_index, dev_batch.batch)
                    loss = self.compute_loss(outputs, dev_batch.y)
                    total_loss += loss.item() * dev_batch.num_graphs
                    total_correct += (outputs.argmax(1) == dev_batch.y).sum().item()
                    total_samples += dev_batch.num_graphs
            avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
            accuracy = total_correct / total_samples if total_samples > 0 else 0.0
        finally:
            if was_training:
                model.train()
        return Metrics(loss=avg_loss, accuracy=accuracy)


class CharNGramTask(DomainTask):
    """Synthetic task: Predict next character from previous N chars.

    Dataset: Deterministic repeating patterns or simple probabilistic grammar.
    Input: [B, SeqLen] (indices)
    Output: [B, VocabSize] (logits for last char)
    """

    def __init__(
        self,
        name: str = "char_ngram",
        device: str = "cpu",
        quick_mode: bool = False,
        vocab_size: int = 27,
        context_len: int = 3,
        **kwargs,
    ):
        super().__init__(name, device=device, quick_mode=quick_mode, **kwargs)
        self.vocab_size = vocab_size
        self.context_len = context_len
        self._input_dim = context_len
        self._output_dim = vocab_size
        self.pattern = torch.arange(vocab_size)

    @property
    def domain_type(self) -> DomainType:
        return DomainType.LM

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.LM,
            description="Character n-gram language modeling",
            default_metrics=["loss", "perplexity"],
            supported_tasks=["language_modeling"],
            default_batch_size=32,
            default_lr=1e-3,
            requires_sequence=True,
            tags=["lm", "character", "ngram"],
        )

    def setup(self) -> None:
        self._setup_done = True

    def get_dataloader(self, split: TaskSplit) -> DataLoader:
        # CharNGramTask uses get_batch instead of DataLoader
        # Return a dummy loader that will be overridden by get_batch
        if not self._setup_done:
            self.setup()
        if self._train_loader is None:
            from torch.utils.data import DataLoader, TensorDataset

            # Create dummy data for DataLoader interface
            dummy_x = torch.zeros(1, self.context_len)
            dummy_y = torch.zeros(1, dtype=torch.long)
            dummy_ds = TensorDataset(dummy_x, dummy_y)
            self._train_loader = DataLoader(dummy_ds, batch_size=1)
            self._val_loader = DataLoader(dummy_ds, batch_size=1)
        if split == TaskSplit.TRAIN:
            return self._train_loader
        return self._val_loader

    def get_batch(
        self, split: str | TaskSplit = "train", batch_size: int = 32
    ) -> tuple[torch.Tensor, torch.Tensor]:
        starts = torch.randint(0, self.vocab_size - self.context_len, (batch_size,))
        x_list: list[torch.Tensor] = []
        y_list: list[torch.Tensor] = []
        for s in starts:
            seq = (
                torch.arange(s.item(), s.item() + self.context_len + 1)
                % self.vocab_size
            )
            x_list.append(seq[:-1])
            y_list.append(seq[-1])
        x = torch.stack(x_list).to(self.device).float().unsqueeze(2)
        x = x.view(x.size(0), -1)
        y = torch.stack(y_list).to(self.device).long()
        return x, y

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
                for i, (batch_inputs, batch_targets) in enumerate(loader):
                    if max_batches and i >= max_batches:
                        break
                    dev_inputs = batch_inputs.to(self.device)
                    dev_targets = batch_targets.to(self.device)
                    outputs = model(dev_inputs)
                    loss = self.compute_loss(outputs, dev_targets)
                    total_loss += loss.item() * dev_inputs.size(0)
                    total_correct += (outputs.argmax(1) == dev_targets).sum().item()
                    total_samples += dev_inputs.size(0)
            avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
            accuracy = total_correct / total_samples if total_samples > 0 else 0.0
        finally:
            if was_training:
                model.train()
        return Metrics(loss=avg_loss, accuracy=accuracy)

    def create_trainer(self, model: nn.Module, **kwargs) -> _TaskTrainer:
        kwargs.pop("device", None)
        return _TaskTrainer(model, self, device=str(self.device), **kwargs)

    def compute_metrics(
        self, logits: torch.Tensor, y: torch.Tensor, loss: float
    ) -> dict[str, float]:
        return {"loss": loss}


def _parse_split_digits(task_name: str) -> tuple[list[int] | None, str]:
    """Parse 'mnist_01' into ([0, 1], 'mnist'). Returns (None, task_name) if no digits."""
    if "_" not in task_name or not any(c.isdigit() for c in task_name):
        return None, task_name

    parts = task_name.split("_")
    digits: list[int] = []
    clean_name_parts: list[str] = []
    for p in parts:
        if p.isdigit():
            for d in p:
                digits.append(int(d))
        elif p == "split":
            continue
        else:
            clean_name_parts.append(p)

    if not digits:
        return None, task_name

    included_classes = sorted(set(digits))
    base_name = "_".join(clean_name_parts)
    if "mnist" in task_name and "mnist" not in base_name:
        base_name = "mnist"
    elif "cifar" in task_name and "cifar" not in base_name:
        base_name = "cifar10"

    return included_classes, base_name


def _normalize_vision_name(base_name: str) -> str:  # ruff: ignore[too-many-return-statements]
    """Normalize a vision dataset name to the canonical key."""
    match base_name:
        case n if "kmnist" in n or "kuzushiji" in n:
            return "kmnist"
        case n if "cifar" in n:
            return "cifar100" if "100" in n else "cifar10"
        case n if "fashion" in n:
            return "fashion_mnist"
        case n if "digits" in n:
            return "digits"
        case n if "usps" in n:
            return "usps"
        case n if "svhn" in n:
            return "svhn"
        case n if "mnist" in n:
            return "mnist"
        case _:
            return base_name


def create_task(  # ruff: ignore[too-many-return-statements, complex-structure]
    task_name: str, device: str = "cpu", quick_mode: bool = False, **kwargs
) -> DomainTask:
    """Factory function for tasks. Maps string names to Task classes via heuristics.

    ``quick_mode=True`` defaults DataLoader ``num_workers`` to 0 (forkserver
    race mitigation, D7 precedent) unless overridden via kwargs.
    """
    if quick_mode and "num_workers" not in kwargs:
        kwargs["num_workers"] = 0
    match task_name:
        case "char_ngram":
            return CharNGramTask(name=task_name, device=device, quick_mode=quick_mode)
        case "pendulum":
            from computronium.domains.rl import RLTask

            return RLTask(
                name=task_name, env_id="Pendulum-v1", device=str(device), **kwargs
            )
        case "acrobot":
            from computronium.domains.rl import RLTask

            return RLTask(
                name=task_name, env_id="Acrobot-v1", device=str(device), **kwargs
            )
        case "cartpole" | "rl":
            from computronium.domains.rl import RLTask

            return RLTask(
                name=task_name, env_id="CartPole-v1", device=str(device), **kwargs
            )
        case "shakespeare" | "tiny_shakespeare":
            from computronium.domains.lm import LMTask

            return LMTask(
                name=task_name,
                dataset_name="tiny_shakespeare",
                device=str(device),
                **kwargs,
            )
        case "xor" | "spiral" | "circles":
            from computronium.domains.vision import VisionTask

            return VisionTask(
                name=task_name,
                dataset_name=task_name,
                device=str(device),
                **kwargs,
            )
        case "sequential_mnist":
            return SequentialMNISTTask(
                name=task_name, device=str(device), quick_mode=quick_mode, **kwargs
            )
        case "copy_task":
            return CopyTask(
                name=task_name, device=str(device), quick_mode=quick_mode, **kwargs
            )
        case "synthetic_forecast":
            from computronium.domains.timeseries import TimeSeriesTask

            return TimeSeriesTask(
                name=task_name,
                dataset_name="synthetic",
                device=str(device),
                quick_mode=quick_mode,
                **kwargs,
            )
        case "graph_classification":
            return GraphClassificationTask(
                name=task_name, device=str(device), quick_mode=quick_mode, **kwargs
            )
        case _:
            _included_classes, base_name = _parse_split_digits(task_name)

    VISION_KEYWORDS = {"vision", "mnist", "cifar", "fashion", "usps", "svhn", "digits"}

    if any(kw in base_name for kw in VISION_KEYWORDS):
        from computronium.domains.vision import VisionTask

        name = _normalize_vision_name(base_name)
        return VisionTask(
            name=name,
            dataset_name=name,
            device=str(device),
            **kwargs,
        )

    match base_name:
        case "cora" | "pubmed" | "citeseer":
            from computronium.domains.graph import GraphTask

            return GraphTask(
                name=base_name, dataset_name=base_name, device=str(device), **kwargs
            )
        case "breast_cancer" | "california_housing" | "iris" | "wine":
            from computronium.domains.tabular import TabularTask

            return TabularTask(
                name=base_name, dataset_name=base_name, device=str(device), **kwargs
            )
        case _:
            raise ValueError(
                f"Unknown task '{task_name}': no resolution path; "
                "available names are in domains.registry.SUPPORTED_TASKS "
                "(no silent fallback to the LM lane)"
            )
