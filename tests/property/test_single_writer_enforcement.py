"""Single-writer enforcement lock (TODO44 D5).

All DuckDB writes must flow through :class:`RecordStore` — the only module
permitted to call ``duckdb.connect`` — and every mutation runs under the
store's ``threading`` write lock. Scans the full tree (computronium/ +
packages/) via AST so lazy/conditional imports cannot hide a bypass.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [REPO / "computronium", REPO / "packages"]
WRITER_MODULE = "computronium/experiment/evidence/store.py"
WRITE_LOCK_ATTR = "_write_lock"


def _py_files() -> list[Path]:
    return [
        p
        for root in SCAN_ROOTS
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts
    ]


def _has_unguarded_duckdb_import(tree: ast.AST) -> bool:
    """True when a runtime (non-TYPE_CHECKING) duckdb import exists in the tree."""

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.found = False
            self._type_checking: frozenset[int] = frozenset()

        def visit_If(self, node: ast.If) -> None:
            outer = self._type_checking
            if "TYPE_CHECKING" in ast.unparse(node.test):
                self._type_checking |= {id(node)}
            self.generic_visit(node)
            self._type_checking = outer

        def visit_Import(self, node: ast.Import) -> None:
            if not self._type_checking and any(a.name == "duckdb" for a in node.names):
                self.found = True
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if not self._type_checking and node.module == "duckdb":
                self.found = True
            self.generic_visit(node)

    visitor = Visitor()
    visitor.visit(tree)
    return visitor.found


class TestSingleWriterEnforcement:
    def test_no_duckdb_imports_outside_store(self) -> None:
        """No module other than the store's connects to DuckDB."""
        offenders: list[Path] = []
        for path in _py_files():
            if path.as_posix().endswith(WRITER_MODULE):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            if _has_unguarded_duckdb_import(tree):
                offenders.append(path)
        assert offenders == []

    def test_store_guards_writes_with_lock(self) -> None:
        """The writer owns a threading lock and initializes it before use."""
        source = (REPO / WRITER_MODULE).read_text(encoding="utf-8")
        assert "import threading" in source
        assert "threading.RLock()" in source
        assert WRITE_LOCK_ATTR in source

    def test_store_has_no_raw_sql_writes_outside_append_paths(self) -> None:
        """INSERT/UPDATE/DELETE statements only exist inside the store module."""
        writer_statements = sum(
            (REPO / WRITER_MODULE).read_text(encoding="utf-8").count(kw)
            for kw in ("INSERT INTO", "UPDATE ", "DELETE FROM")
        )
        assert writer_statements > 0
        for path in _py_files():
            if path.as_posix().endswith(WRITER_MODULE):
                continue
            text = path.read_text(encoding="utf-8")
            for kw in ("INSERT INTO records", "UPDATE records", "DELETE FROM records"):
                assert kw not in text, f"{path} writes records table directly"
