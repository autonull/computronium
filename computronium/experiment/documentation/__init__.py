"""Experiment Documentation Package.

Living documentation infrastructure:
- Experiment Catalog: Queryable catalog of all runs/records
- Method Cards: Auto-generated documentation for all ontology primitives
- FAQ/Troubleshooting: Curated from CI/CD failures and user reports
"""

from computronium.experiment.documentation.catalog import (
    CatalogEntry,
    RecordEntry,
    build_catalog,
    export_catalog,
    export_records,
    query_records,
)
from computronium.experiment.documentation.catalog import (
    main as catalog_main,
)
from computronium.experiment.documentation.faq import (
    FAQEntry,
    generate_faq,
)
from computronium.experiment.documentation.faq import (
    main as faq_main,
)
from computronium.experiment.documentation.method_cards import (
    MethodCard,
    generate_method_cards,
)
from computronium.experiment.documentation.method_cards import (
    main as method_cards_main,
)

__all__ = [
    "CatalogEntry",
    "FAQEntry",
    "MethodCard",
    "RecordEntry",
    "build_catalog",
    "catalog_main",
    "export_catalog",
    "export_records",
    "faq_main",
    "generate_faq",
    "generate_method_cards",
    "method_cards_main",
    "query_records",
]
