"""Adapter: single source is ceec.migrate.todo18_records (Rule 6).

Module-aliased (sys.modules) so attribute patching (e.g. pytest monkeypatch
of TODO18_CLAIM_RECORDS in legacy tests) hits the real package module.
"""

from __future__ import annotations

import sys

from ceec.migrate import todo18_records as _source

sys.modules[__name__] = _source
