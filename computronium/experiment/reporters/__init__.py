"""Experiment reporters package.

Provides output formats for experiment results:
- HTML: Rich interactive reports with Pareto frontiers, heatmaps, clustering
- JSON: Structured machine-readable output
"""

from computronium.experiment.reporters.html import (
    ReportConfig,
    generate_html_report,
    generate_report_from_db,
)
from computronium.experiment.reporters.json import (
    JSONReportConfig,
    generate_json_report,
    generate_json_report_from_db,
)

__all__ = [
    "JSONReportConfig",
    "ReportConfig",
    "generate_html_report",
    "generate_json_report",
    "generate_json_report_from_db",
    "generate_report_from_db",
]
