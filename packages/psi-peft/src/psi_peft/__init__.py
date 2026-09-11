"""Psi-PEFT — frozen-backbone task switching with temporal-psi readouts.

A frozen backbone acquires, switches, and re-acquires tasks through a
lightweight closed-form ψ readout; θ is never edited. Extracted from the
Computronium project (X-TPC-001..003, X-TAC-001 validated scope).
"""

from __future__ import annotations

from psi_peft.adaptive import AdaptivePsiReadout
from psi_peft.buffered import BufferedPsiReadout
from psi_peft.readout import PsiReadout

__all__ = ["AdaptivePsiReadout", "BufferedPsiReadout", "PsiReadout"]
