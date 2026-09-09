"""Harvest the I(C,U) table from recorded logs into data/icu_measurements.csv.

Zero new compute: every row cites an existing log (TODO16 §0.2). Sources
without a recorded log (w7 STDP, w0 transformer locals, PEPITA CIFAR/Cora)
are reported as missing, never fabricated.
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOGS = ROOT / "logs"
OUT = ROOT / "data" / "icu_measurements.csv"


@dataclass(frozen=True, slots=True)
class ICURecord:
    credit: str
    update: str
    geometry: str
    depth: int
    width: int
    task: str
    seed: int
    accuracy: float
    interaction_i: float
    mechanism_class: str
    plasticity: str
    status: str
    source: str


ARM_CREDIT = {
    "bp": "bp",
    "pepita": "pepita",
    "ff": "ff",
    "rp_weak": "fa",
    "rp_ortho": "fa",
    "rp_vweak": "fa",
    "rp": "fa",
    "local": "local_contrastive",
    "local3": "local_contrastive",
    "local2": "local_contrastive",
    "bptt": "bptt",
    "eqprop": "eqprop",
}
MECHANISM = {
    "bp": "exact_gradient",
    "fa": "projected_pseudo",
    "pepita": "projected_pseudo",
    "local_contrastive": "goodness_contrast",
    "ff": "goodness_contrast",
    "bptt": "exact_gradient",
    "eqprop": "exact_gradient",
}

LADDER_RE = re.compile(
    r"^\s*(?P<credit>[\w]+)\s+x\s+(?P<update>[\w.]+):\s+(?P<acc>[\d.]+)\s+±"
    r".*?\[(?P<seeds>[^\]]+)\]"
)
ICU_RE = re.compile(
    r"^\s*(?P<credit>[\w]+):\s+Δ(?:_(?P<named>\w+))?\s+[+-][\d.]+\s+"
    r"I\(C,U\)\s+(?P<icu>[+-][\d.]+)"
)
NCA_RE = re.compile(
    r"(?P<arm>[\w]+) x (?P<update>[\w_]+) \(lr [\d.]+\) seed (?P<seed>\d+):"
    r" MSE (?P<mse>[\d.]+) fg-acc (?P<acc>[\d.]+)"
)
NTM_STEP_RE = re.compile(
    r"^\s*[\w]+ step \d+: loss [\d.]+ copy-acc\(fresh\) (?P<acc>[\d.]+)"
)
DEPTH_RE = re.compile(
    r"^(?P<credit>[\w]+) d (?P<depth>\d+): best (?P<best>[\d.]+) @ (?P<step>\d+)"
    r" restored (?P<restored>[\d.]+) EMA (?P<ema>[\d.]+)"
)
HARVEST_RE = re.compile(r"best val (?P<best>[\d.]+) @ batch (?P<step>\d+)")
EMA_RE = re.compile(r"EMA\([\d.]+\) final val (?P<ema>[\d.]+)")
PEPITA_RE = re.compile(
    r"^\s+(?P<arm>bp/adam|pepita/adam|pepita/muon\.02):\s+(?P<mean>[\d.]+)\s+"
    r"\[(?P<seeds>[^\]]+)\]"
)
ORD_MEAN_RE = re.compile(
    r"^\s+(?P<arm>[\w]+):\s+mean (?P<mean>[\d.]+)\s+\[(?P<seeds>[^\]]+)\]"
)


def _parse_campaign(path: Path) -> list[ICURecord]:
    """Campaign 7.1 cells (TODO16 §7.1): 3 plasticities × 4 credits ×
    2 updates × 3 seeds on d32 MNIST — the ψ-modulation rows the CSV
    schema's plasticity field was created for."""
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        # arms are column-aligned with variable whitespace — parse by split
        parts = line.split()
        if len(parts) != 8 or parts[1] != "x" or parts[3] != "x" or parts[5] != "seed":
            continue
        plasticity, credit_raw, update, seed, acc = (
            parts[0],
            parts[2],
            parts[4],
            parts[6].rstrip(":"),
            parts[7],
        )
        if not seed.isdigit():
            continue
        credit = ARM_CREDIT.get(credit_raw, credit_raw)
        rows.append(
            ICURecord(
                credit=credit,
                update="muon" if update == "muon" else "ortho",
                geometry="mlp",
                depth=32,
                width=128,
                task="mnist",
                seed=int(seed),
                accuracy=float(acc),
                interaction_i=0.0,
                mechanism_class=MECHANISM.get(credit, "other"),
                plasticity=plasticity,
                status="promoted" if float(acc) >= 0.75 else "boundary",
                source=path.name,
            )
        )
    return rows


def _seeds(raw: str) -> list[tuple[int, float]]:
    accs = [float(a.strip().strip(chr(39))) for a in raw.split(",")]
    return list(enumerate(accs))


def _parse_ladder(
    path: Path,
    geometry: str,
    task: str,
    depth: int,
    width: int,
    status: str,
    default_update: str = "muon",
) -> list[ICURecord]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    icu: dict[tuple[str, str], float] = {}
    for line in text.splitlines():
        if m := ICU_RE.match(line):
            update = m["named"] or default_update
            icu[ARM_CREDIT.get(m["credit"], m["credit"]), update.rstrip(".2")] = float(
                m["icu"]
            )
    rows: list[ICURecord] = []
    for line in text.splitlines():
        m = LADDER_RE.match(line)
        if m:
            credit = ARM_CREDIT.get(m["credit"], m["credit"])
            update = m["update"].rstrip(".2")
            for seed, acc in _seeds(m["seeds"]):
                rows.append(
                    ICURecord(
                        credit=credit,
                        update=update,
                        geometry=geometry,
                        depth=depth,
                        width=width,
                        task=task,
                        seed=seed,
                        accuracy=acc,
                        interaction_i=icu.get((credit, update), 0.0),
                        mechanism_class=MECHANISM.get(credit, "other"),
                        plasticity="null",
                        status=status,
                        source=path.name,
                    )
                )
    return rows


def _parse_nca(paths: list[Path]) -> list[ICURecord]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            m = NCA_RE.search(line)
            if m:
                rows.append(
                    ICURecord(
                        credit=ARM_CREDIT.get(m["arm"], m["arm"]),
                        update=m["update"],
                        geometry="nca",
                        depth=1,
                        width=16,
                        task="ordinary",
                        seed=int(m["seed"]),
                        accuracy=float(m["acc"]),
                        interaction_i=0.0,
                        mechanism_class=MECHANISM.get(
                            ARM_CREDIT.get(m["arm"], m["arm"]), "other"
                        ),
                        plasticity="null",
                        status="boundary",
                        source=path.name,
                    )
                )
    return rows


def _parse_ntm(paths: list[Path], steps: int, status: str) -> list[ICURecord]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        accs = [
            float(m["acc"])
            for line in path.read_text(encoding="utf-8").splitlines()
            if (m := NTM_STEP_RE.match(line))
        ]
        seed = 0
        if m_seed := re.search(r"_s(\d+)\.log$", path.name):
            seed = int(m_seed.group(1))
        if accs:
            rows.append(
                ICURecord(
                    credit=ARM_CREDIT["local3" if "local" in path.name else "bptt"],
                    update="adam",
                    geometry="ntm",
                    depth=1,
                    width=16,
                    task="copy",
                    seed=seed,
                    accuracy=accs[-1],
                    interaction_i=0.0,
                    mechanism_class=MECHANISM["local_contrastive"]
                    if "local" in path.name
                    else MECHANISM["bptt"],
                    plasticity="null",
                    status=status,
                    source=path.name,
                )
            )
    return rows


def _parse_family_depth(paths: list[Path], task: str) -> list[ICURecord]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            m = DEPTH_RE.match(line)
            if m and m["credit"] in {"eqprop", "ff"}:
                rows.append(
                    ICURecord(
                        credit=m["credit"],
                        update="euclid",
                        geometry="mlp",
                        depth=int(m["depth"]),
                        width=128,
                        task=task,
                        seed=0,
                        accuracy=float(m["ema"]),
                        interaction_i=0.0,
                        mechanism_class=MECHANISM[m["credit"]],
                        plasticity="null",
                        status="boundary",
                        source=path.name,
                    )
                )
    return rows


def _parse_depth_harvest(
    paths: list[Path], depth: int, task: str, gate: float
) -> list[ICURecord]:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        best = HARVEST_RE.search(text)
        ema = EMA_RE.search(text)
        if not best:
            continue
        seed = 0
        if m_seed := re.search(r"_s(\d+)\.log$", path.name):
            seed = int(m_seed.group(1))
        rows.append(
            ICURecord(
                credit="bp",
                update="ortho_adam",
                geometry="mlp",
                depth=depth,
                width=128,
                task=task,
                seed=seed,
                accuracy=float(ema["ema"]) if ema else float(best["best"]),
                interaction_i=0.0,
                mechanism_class="exact_gradient",
                plasticity="null",
                status="promoted"
                if (ema and float(ema["ema"]) >= gate)
                else "boundary",
                source=path.name,
            )
        )
    return rows


def _parse_pepita_breadth(
    path: Path, task: str, din: int, dout: int
) -> list[ICURecord]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = PEPITA_RE.match(line)
        if m:
            credit = "bp" if m["arm"].startswith("bp") else "pepita"
            update = "adam" if "adam" in m["arm"] else "muon"
            for seed, acc in _seeds(m["seeds"]):
                rows.append(
                    ICURecord(
                        credit=credit,
                        update=update,
                        geometry="mlp",
                        depth=2,
                        width=256,
                        task=task,
                        seed=seed,
                        accuracy=acc,
                        interaction_i=0.0,
                        mechanism_class=MECHANISM[credit],
                        plasticity="null",
                        status="promoted",
                        source=path.name,
                    )
                )
    return rows


def _parse_ordinary_mean(path: Path) -> list[ICURecord]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ORD_MEAN_RE.match(line)
        if m:
            for seed, acc in _seeds(m["seeds"]):
                rows.append(
                    ICURecord(
                        credit=ARM_CREDIT.get(m["arm"], m["arm"]),
                        update="adam",
                        geometry="ntm",
                        depth=1,
                        width=32,
                        task="ordinary",
                        seed=seed,
                        accuracy=acc,
                        interaction_i=0.0,
                        mechanism_class=MECHANISM.get(
                            ARM_CREDIT.get(m["arm"], m["arm"]), "other"
                        ),
                        plasticity="null",
                        status="promoted",
                        source=path.name,
                    )
                )
    return rows


def collect() -> list[ICURecord]:
    rows: list[ICURecord] = []
    rows += _parse_ladder(
        LOGS / "w1_credit_ladder.log", "mlp", "mnist", 2, 128, "promoted"
    )
    rows += _parse_ladder(
        LOGS / "w1_credit_ladder_lion.log", "mlp", "mnist", 2, 128, "promoted"
    )
    rows += _parse_ladder(
        LOGS / "w1_credit_ladder_ext.log", "mlp", "mnist", 2, 128, "promoted"
    )
    rows += _parse_ladder(
        LOGS / "w1_lattice_ladder.log",
        "lattice",
        "mnist",
        2,
        128,
        "boundary",
        default_update="ortho",
    )

    rows += _parse_nca([LOGS / "w8_nca_verdict.log", LOGS / "w8_ortho_screen.log"])
    rows += _parse_ntm(
        [
            LOGS / f"w8_ntm_promo_r6_{arm}_s{s}.log"
            for arm in ("local3", "bptt")
            for s in range(3)
        ],
        3000,
        "promoted",
    )
    rows += _parse_ntm(
        [LOGS / f"breadth_ntm_copy8k_s{s}.log" for s in range(3)], 8000, "promoted"
    )
    rows += _parse_family_depth(
        [LOGS / f"w9_family_depth_grid{v}.log" for v in ("", 2, 3, 4, 5)], "mnist"
    )
    rows += _parse_depth_harvest(
        [LOGS / f"d100_harvest_s{s}.log" for s in range(3)], 100, "mnist", 0.75
    )
    rows += _parse_depth_harvest(
        [LOGS / "breadth_d50_fashion.log"], 50, "fashion", 0.75
    )
    rows += _parse_pepita_breadth(LOGS / "w16_pepita_cifar10.log", "cifar10", 3072, 10)
    rows += _parse_pepita_breadth(LOGS / "w16_pepita_cora.log", "cora", 1433, 7)
    rows += _parse_ordinary_mean(LOGS / "w8_lstm_control.log")
    rows += _parse_campaign(LOGS / "w16_campaign_A_s0.log")
    rows += _parse_campaign(LOGS / "w16_campaign_A_s1.log")
    rows += _parse_campaign(LOGS / "w16_campaign_A_s2.log")
    rows += _parse_campaign(LOGS / "w16_campaign_B_s0.log")
    rows += _parse_campaign(LOGS / "w16_campaign_B_s1.log")
    rows += _parse_campaign(LOGS / "w16_campaign_B_s2.log")
    rows += _parse_campaign(LOGS / "w16_campaign_C_s0.log")
    rows += _parse_campaign(LOGS / "w16_campaign_C_s1.log")
    rows += _parse_campaign(LOGS / "w16_campaign_C_s2.log")
    return rows


MISSING_SOURCES = [
    "logs/w7_stdp_muon.log (STDP x muon — no recorded log found)",
    "logs/w0_tf_local_optimizers.log (transformer local credit — no recorded log found)",
    "d19_depth_harvest gallery record (docs/figures/run_records, not a log)",
    "d50_autopsy depth grid — breadth_d50_* only partially recorded (digits/fashion)",
]


def main() -> int:
    rows = collect()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(r) for r in rows)
    print(f"wrote {len(rows)} rows -> {OUT.relative_to(ROOT)}")
    for src in MISSING_SOURCES:
        print(f"missing: {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
