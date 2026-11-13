"""
Language Modeling Domain Tasks

Standard LM datasets (Shakespeare, WikiText, etc.)
"""

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from computronium.domains.base import (
    DomainSpec,
    DomainTask,
    DomainType,
    Metrics,
    TaskSplit,
)

__all__ = [
    "LMTask",
]


class _NextTokenDataset(Dataset):
    """Contiguous next-token pairs over a token tensor.

    One item is ``(tokens[i : i+T], tokens[i+1 : i+T+1])`` and the stride is
    ``T``, so no token is shared between items and a validation pass covers
    its split once. A bare ``DataLoader`` over the token tensor yields single
    tensors, which the system trainer cannot unpack into ``(x, y)``.
    """

    def __init__(self, tokens: torch.Tensor, seq_len: int) -> None:
        self.tokens = tokens
        self.seq_len = seq_len
        self._count = max(0, (len(tokens) - 1) // seq_len)

    def __len__(self) -> int:
        return self._count

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        start = index * self.seq_len
        chunk = self.tokens[start : start + self.seq_len + 1]
        return chunk[:-1], chunk[1:]


class LMTask(DomainTask):
    """Language modeling domain tasks."""

    def __init__(
        self,
        name: str = "tiny_shakespeare",
        dataset_name: str = "tiny_shakespeare",
        seq_len: int = 128,
        vocab_size: int | None = None,
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self.dataset_name = dataset_name
        self.seq_len = seq_len
        self.vocab_size = vocab_size

    @property
    def domain_type(self) -> DomainType:
        return DomainType.LM

    @property
    def spec(self) -> DomainSpec:
        return DomainSpec(
            name=self.name,
            domain_type=DomainType.LM,
            description=f"Language modeling: {self.dataset_name}",
            default_metrics=["perplexity", "loss", "accuracy"],
            supported_tasks=["language_modeling", "text_generation"],
            default_batch_size=32,
            default_lr=3e-4,
            requires_sequence=True,
            tags=["nlp", "language"],
        )

    def setup(self) -> None:
        """Load LM dataset."""
        # Use existing dataset loading from computronium.datasets
        from computronium.data.lm import get_lm_dataset

        dataset = get_lm_dataset(self.dataset_name, seq_len=self.seq_len)
        data = dataset.data
        self.vocab_size = self.vocab_size or dataset.vocab_size
        self._output_dim = self.vocab_size
        self._input_dim = self.seq_len  # token indices

        # Split train/val
        n = int(0.9 * len(data))
        train_data = data[:n]
        val_data = data[n:]
        self._train_data = train_data
        self._val_data = val_data

        # Create DataLoaders over next-token pairs; the trainer unpacks (x, y)
        self._train_loader = DataLoader(
            _NextTokenDataset(train_data, self.seq_len),
            batch_size=self.batch_size,
            shuffle=True,
        )
        self._val_loader = DataLoader(
            _NextTokenDataset(val_data, self.seq_len),
            batch_size=self.batch_size,
            shuffle=False,
        )
        self._test_loader = self._val_loader
        self._setup_done = True

    def get_dataloader(self, split: TaskSplit) -> DataLoader:
        if not self._setup_done:
            self.setup()
        loader = self._train_loader if split == TaskSplit.TRAIN else self._val_loader
        if loader is None:
            msg = f"{self.name}: setup() built no loader for {split}"
            raise RuntimeError(msg)
        return loader

    def get_batch(
        self, split: str | TaskSplit = "train", batch_size: int | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Get a batch of (inputs, targets) for LM training.

        Returns inputs [B, seq_len] and targets [B, seq_len] for autoregressive
        next-token prediction at each position.
        """
        if not self._setup_done:
            self.setup()

        bsz = batch_size or self.batch_size
        if isinstance(split, str):
            data = self._train_data if split == "train" else self._val_data
        else:
            data = self._train_data if split == TaskSplit.TRAIN else self._val_data

        idx = torch.randint(0, len(data) - self.seq_len - 1, (bsz,))
        x = torch.stack([data[i : i + self.seq_len] for i in idx]).to(self.device)
        y = torch.stack([data[i + 1 : i + 1 + self.seq_len] for i in idx]).to(
            self.device
        )
        return x, y

    def evaluate(
        self,
        model: nn.Module,
        split: TaskSplit = TaskSplit.VAL,
        max_batches: int | None = None,
    ) -> Metrics:
        import numpy as np

        model.eval()
        loader = self.get_dataloader(split)

        total_loss = 0.0
        total_correct = 0
        total_tokens = 0

        with torch.no_grad():
            for i, batch in enumerate(loader):
                if max_batches and i >= max_batches:
                    break

                if isinstance(batch, (list, tuple)):
                    inputs, targets = batch
                else:
                    inputs = batch[:, :-1]
                    targets = batch[:, 1:]

                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = model(inputs)

                outputs, targets = self._flat(outputs, targets)
                loss = self.compute_loss(outputs, targets)

                total_loss += loss.item() * targets.numel()
                total_correct += (outputs.argmax(1) == targets).sum().item()
                total_tokens += targets.numel()

        avg_loss = total_loss / total_tokens if total_tokens > 0 else 0.0
        accuracy = total_correct / total_tokens if total_tokens > 0 else 0.0
        perplexity = np.exp(min(avg_loss, 10))

        return Metrics(loss=avg_loss, accuracy=accuracy, perplexity=perplexity)

    @staticmethod
    def _flat(
        outputs: torch.Tensor, targets: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Fold a sequence-shaped logits/target pair to one row per token.

        ``TransformerGeometry`` already folds ``[B, T]`` into ``[B*T, V]``; a
        second reshape then mismatched 4096 logits against 32 target rows.
        """
        from computronium.ontology._utils import _align_target_rows

        if outputs.dim() == 3:
            outputs = outputs.reshape(-1, outputs.size(-1))
        return outputs, _align_target_rows(outputs, targets)

    def compute_loss(
        self, outputs: torch.Tensor, targets: torch.Tensor
    ) -> torch.Tensor:
        outputs, targets = self._flat(outputs, targets)
        return torch.nn.functional.cross_entropy(outputs, targets)
