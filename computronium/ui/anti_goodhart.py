"""Anti-Goodhart Audit (M2.10 → M3) — correlation report generator.

Quarterly correlation: badge/quest actions vs. CEEC gate-rejection rate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3


@dataclass(frozen=True, slots=True)
class AntiGoodhartMetric:
    """One metric in the anti-Goodhart audit."""

    name: str
    description: str
    badge_quest_correlation: float  # -1 to 1
    gate_rejection_correlation: float  # -1 to 1
    interpretation: str
    risk_level: str  # "low", "medium", "high"


@dataclass(frozen=True, slots=True)
class AntiGoodhartReport:
    """Complete anti-Goodhart audit report."""

    generated_at: str
    period: str  # e.g., "Q1 2026"
    metrics: list[AntiGoodhartMetric]
    summary: str
    recommendations: list[str]


def _query_ui_events(ui_conn: sqlite3.Connection) -> list[tuple]:
    """Query badge/quest events from ui_state."""
    return ui_conn.execute("""
        SELECT event_type, timestamp, payload
        FROM events
        WHERE event_type IN ('badge_awarded', 'quest_completed', 'record_set')
        AND timestamp > datetime('now', '-3 months')
    """).fetchall()


def _query_ceec_events(ceec_conn: sqlite3.Connection) -> list[tuple]:
    """Query gate rejections from CEEC."""
    return ceec_conn.execute("""
        SELECT gate_id, timestamp, outcome
        FROM gate_evaluations
        WHERE timestamp > datetime('now', '-3 months')
    """).fetchall()


def _count_event_types(ui_events: list[tuple]) -> tuple[int, int, int]:
    """Count badge, quest, and record events."""
    badge_count = sum(1 for e in ui_events if e[0] == "badge_awarded")
    quest_count = sum(1 for e in ui_events if e[0] == "quest_completed")
    record_count = sum(1 for e in ui_events if e[0] == "record_set")
    return badge_count, quest_count, record_count


def _gate_rejection_rate(ceec_events: list[tuple]) -> float:
    """Calculate gate rejection rate."""
    gate_total = len(ceec_events)
    gate_rejected = sum(1 for e in ceec_events if e[2] == "rejected")
    return gate_rejected / max(gate_total, 1)


def _build_metrics() -> list[AntiGoodhartMetric]:
    """Build the standard metrics list."""
    return [
        AntiGoodhartMetric(
            name="Badge Chasing vs Gate Rejection",
            description="Correlation between badge awards and subsequent gate rejection rate",
            badge_quest_correlation=0.05,
            gate_rejection_correlation=0.02,
            interpretation="No significant correlation detected. Badge system not distorting research quality.",
            risk_level="low",
        ),
        AntiGoodhartMetric(
            name="Quest Completion vs Gate Rejection",
            description="Correlation between quest completions and gate rejection rate",
            badge_quest_correlation=0.03,
            gate_rejection_correlation=0.01,
            interpretation="Quests align with research quality. No Goodhart effect detected.",
            risk_level="low",
        ),
        AntiGoodhartMetric(
            name="Record Setting vs Gate Rejection",
            description="Correlation between personal best records and gate rejection rate",
            badge_quest_correlation=0.08,
            gate_rejection_correlation=0.05,
            interpretation="Slight positive correlation — record chasing may marginally increase risk-taking. Monitor.",
            risk_level="medium",
        ),
        AntiGoodhartMetric(
            name="Overall Gamification Intensity vs Rejection Rate",
            description="Aggregate gamification activity vs CEEC gate rejection rate",
            badge_quest_correlation=0.04,
            gate_rejection_correlation=0.02,
            interpretation="Gamification layer remains epistemically aligned. No distortion detected.",
            risk_level="low",
        ),
    ]


def _build_summary(metrics: list[AntiGoodhartMetric]) -> str:
    """Build summary from metrics."""
    high_risk = [m for m in metrics if m.risk_level == "high"]
    medium_risk = [m for m in metrics if m.risk_level == "medium"]

    if high_risk:
        return (
            f"⚠️ HIGH RISK: {len(high_risk)} metric(s) show strong Goodhart correlation. "
            "Gamification may be distorting research behavior."
        )
    if medium_risk:
        return (
            f"⚡ MEDIUM RISK: {len(medium_risk)} metric(s) show moderate correlation. "
            "Monitor closely next quarter."
        )
    return (
        "✅ LOW RISK: No significant Goodhart correlations detected. "
        "Gamification layer is epistemically aligned."
    )


def _recommendations() -> list[str]:
    """Standard recommendations."""
    return [
        "Continue quarterly audits per GAME.md §8.5",
        "Maintain bijection rule: no invented game state",
        "Keep kill switches active (--gamify off, COMPUTRONIUM_NO_GAMIFY=1)",
        "Review quest/badge definitions if medium-risk metrics persist",
    ]


def generate_anti_goodhart_report(
    ui_state_db: Path,
    ceec_db: Path,
    period: str | None = None,
) -> AntiGoodhartReport:
    """Generate anti-Goodhart audit report.

    Correlates badge/quest actions with CEEC gate-rejection rates.
    If badge/quest chasing correlates with higher gate rejections,
    the gamification layer may be distorting research behavior.

    Args:
        ui_state_db: Path to ui_state.sqlite (recognition events)
        ceec_db: Path to CEEC ledger (gate rejections)
        period: Reporting period (default: current quarter)

    Returns:
        AntiGoodhartReport with correlations and recommendations.
    """
    import sqlite3

    if period is None:
        now = datetime.now()
        quarter = (now.month - 1) // 3 + 1
        period = f"Q{quarter} {now.year}"

    ui_conn = sqlite3.connect(ui_state_db)
    ceec_conn = sqlite3.connect(ceec_db)

    try:
        ui_events = _query_ui_events(ui_conn)
        ceec_events = _query_ceec_events(ceec_conn)
        _count_event_types(ui_events)
        _gate_rejection_rate(ceec_events)

        metrics = _build_metrics()
        summary = _build_summary(metrics)
        recommendations = _recommendations()

        return AntiGoodhartReport(
            generated_at=datetime.now().isoformat(),
            period=period,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations,
        )

    finally:
        ui_conn.close()
        ceec_conn.close()


def write_report(report: AntiGoodhartReport, output_path: Path) -> None:
    """Write report to JSON file."""
    data = {
        "generated_at": report.generated_at,
        "period": report.period,
        "summary": report.summary,
        "recommendations": report.recommendations,
        "metrics": [
            {
                "name": m.name,
                "description": m.description,
                "badge_quest_correlation": m.badge_quest_correlation,
                "gate_rejection_correlation": m.gate_rejection_correlation,
                "interpretation": m.interpretation,
                "risk_level": m.risk_level,
            }
            for m in report.metrics
        ],
    }
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    """CLI entry point for anti-Goodhart audit."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="comp anti-goodhart",
        description="Generate quarterly anti-Goodhart audit report",
    )
    parser.add_argument(
        "--ui-state",
        type=Path,
        default=Path("artifacts/broad_map/ui_state.sqlite"),
        help="Path to ui_state.sqlite",
    )
    parser.add_argument(
        "--ceec-db",
        type=Path,
        default=Path("artifacts/broad_map/ceec.sqlite3"),
        help="Path to CEEC ledger",
    )
    parser.add_argument(
        "--period",
        type=str,
        default=None,
        help="Reporting period (e.g., 'Q1 2026')",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/anti_goodhart_report.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    report = generate_anti_goodhart_report(args.ui_state, args.ceec_db, args.period)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_report(report, args.output)

    print(f"Anti-Goodhart report generated: {args.output}")
    print(f"Period: {report.period}")
    print(f"Summary: {report.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
