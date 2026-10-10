"""Report template system (Phase A).

Jinja2-based templates with Pydantic context models for publication-grade reports.
"""

from computronium.experiment.templates.report.generator import (
    JinjaReportGenerator,
    generate_report_from_store,
)
from computronium.experiment.templates.report.models import (
    AblationResult,
    AxisCoverage,
    CampaignConfig,
    FailureTaxonomy,
    GraphReportContext,
    Hypothesis,
    LanguageReportContext,
    ParetoPoint,
    ReportContext,
    ReportMetadata,
    ReproducibilityInfo,
    RLReportContext,
    StabilityMetrics,
    StatisticalResult,
    TabularReportContext,
    TemplateConfig,
    VisionReportContext,
)

__all__ = [
    # Models
    "ReportContext",
    "ReportMetadata",
    "AxisCoverage",
    "ParetoPoint",
    "StabilityMetrics",
    "FailureTaxonomy",
    "Hypothesis",
    "StatisticalResult",
    "AblationResult",
    "CampaignConfig",
    "ReproducibilityInfo",
    "TemplateConfig",
    # Domain-specific contexts
    "VisionReportContext",
    "RLReportContext",
    "TabularReportContext",
    "GraphReportContext",
    "LanguageReportContext",
    # Generator
    "JinjaReportGenerator",
    "generate_report_from_store",
]
