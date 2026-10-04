"""Legality DSL: expression AST and evaluator for constraint language."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from computronium.experiment.schema.coordinate import Coordinate

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


# Protocol for expression types with to_json method
@runtime_checkable
class Expr(Protocol):
    """Protocol for expression types with to_json method."""

    def to_json(self) -> dict[str, Any]: ...


# Base class for all expression types - using a protocol-like pattern
class _ExprBase:
    """Base marker for expression types."""


@dataclass(frozen=True, slots=True)
class Var(Expr):
    """Variable reference: axis.param or schedule.field"""

    name: str

    def to_json(self) -> dict[str, Any]:
        return {"type": "Var", "name": self.name}


@dataclass(frozen=True, slots=True)
class Const(Expr):
    """Constant value"""

    value: Any

    def to_json(self) -> dict[str, Any]:
        return {"type": "Const", "value": self.value}


@dataclass(frozen=True, slots=True)
class Not(Expr):
    """Logical negation"""

    expr: Expr

    def to_json(self) -> dict[str, Any]:
        return {"type": "Not", "expr": self.expr.to_json()}


@dataclass(frozen=True, slots=True)
class And(Expr):
    """Logical conjunction"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "And",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Or(Expr):
    """Logical disjunction"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Or",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Eq(Expr):
    """Equality comparison"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Eq",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Ne(Expr):
    """Inequality comparison"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Ne",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Lt(Expr):
    """Less than comparison"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Lt",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Le(Expr):
    """Less than or equal comparison"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Le",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Gt(Expr):
    """Greater than comparison"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Gt",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Ge(Expr):
    """Greater than or equal comparison"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Ge",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class In(Expr):
    """Membership test"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "In",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class NotIn(Expr):
    """Non-membership test"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "NotIn",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class HasKey(Expr):
    """Object key existence test"""

    obj: Expr
    key: Expr

    def to_json(self) -> dict[str, Any]:
        return {"type": "HasKey", "obj": self.obj.to_json(), "key": self.key.to_json()}


@dataclass(frozen=True, slots=True)
class Call(Expr):
    """Function call"""

    func: str
    args: tuple[Expr, ...]

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Call",
            "func": self.func,
            "args": [arg.to_json() for arg in self.args],
        }


@dataclass(frozen=True, slots=True)
class Implies(Expr):
    """Logical implication: left implies right"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Implies",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Add(Expr):
    """Addition"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Add",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Sub(Expr):
    """Subtraction"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Sub",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Mul(Expr):
    """Multiplication"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Mul",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Div(Expr):
    """Division"""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Div",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


# =============================================================================
# Population-level DSL extensions (Phase 1-3)
# =============================================================================


@dataclass(frozen=True, slots=True)
class ForAll(Expr):
    """Universal quantification over a filtered population."""

    filter: Expr
    body: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "ForAll",
            "filter": self.filter.to_json(),
            "body": self.body.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Exists(Expr):
    """Existential quantification over a filtered population."""

    filter: Expr
    body: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Exists",
            "filter": self.filter.to_json(),
            "body": self.body.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Mean(Expr):
    """Arithmetic mean of values over a grouped population."""

    expr: Expr
    group_by: tuple[str, ...] = ()

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Mean",
            "expr": self.expr.to_json(),
            "group_by": list(self.group_by),
        }


@dataclass(frozen=True, slots=True)
class Max(Expr):
    """Maximum value over a grouped population."""

    expr: Expr
    group_by: tuple[str, ...] = ()

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Max",
            "expr": self.expr.to_json(),
            "group_by": list(self.group_by),
        }


@dataclass(frozen=True, slots=True)
class Min(Expr):
    """Minimum value over a grouped population."""

    expr: Expr
    group_by: tuple[str, ...] = ()

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Min",
            "expr": self.expr.to_json(),
            "group_by": list(self.group_by),
        }


@dataclass(frozen=True, slots=True)
class Std(Expr):
    """Standard deviation over a grouped population."""

    expr: Expr
    group_by: tuple[str, ...] = ()

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Std",
            "expr": self.expr.to_json(),
            "group_by": list(self.group_by),
        }


@dataclass(frozen=True, slots=True)
class Diff(Expr):
    """Difference between two values (e.g., payload vs baseline)."""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Diff",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Ratio(Expr):
    """Ratio between two values (e.g., baseline / payload)."""

    left: Expr
    right: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Ratio",
            "left": self.left.to_json(),
            "right": self.right.to_json(),
        }


# Phase 2: Hypothesis Templates
@dataclass(frozen=True, slots=True)
class Template(Expr):
    """Parameterized hypothesis template with binding."""

    name: str
    params: tuple[str, ...]
    body: Expr

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Template",
            "name": self.name,
            "params": list(self.params),
            "body": self.body.to_json(),
        }


@dataclass(frozen=True, slots=True)
class Bind(Expr):
    """Instantiate a template with parameter bindings."""

    template: str
    bindings: dict[str, Expr]

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Bind",
            "template": self.template,
            "bindings": {k: v.to_json() for k, v in self.bindings.items()},
        }


# Phase 3: Trajectory Operators
@dataclass(frozen=True, slots=True)
class Eventually(Expr):
    """Eventually operator over trajectory: predicate holds at some step within window."""

    predicate: Expr
    within: int | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Eventually",
            "predicate": self.predicate.to_json(),
            "within": self.within,
        }


@dataclass(frozen=True, slots=True)
class Always(Expr):
    """Always operator over trajectory: predicate holds at all steps."""

    predicate: Expr
    within: int | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Always",
            "predicate": self.predicate.to_json(),
            "within": self.within,
        }


@dataclass(frozen=True, slots=True)
class Monotonic(Expr):
    """Monotonic trajectory: values strictly increase/decrease."""

    expr: Expr
    direction: str  # "increase" or "decrease"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "Monotonic",
            "expr": self.expr.to_json(),
            "direction": self.direction,
        }


_ARITHMETIC_OPS = frozenset({Add, Sub, Mul, Div})
_BINARY_OPS = frozenset({Eq, Ne, Lt, Le, Gt, Ge, In, NotIn})
_QUANTIFIERS = frozenset({ForAll, Exists})
_AGGREGATIONS = frozenset({Mean, Max, Min, Std})
_COMPARATIVE = frozenset({Diff, Ratio})
_TEMPLATES = frozenset({Template, Bind})
_TRAJECTORY_OPS = frozenset({Eventually, Always, Monotonic})


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for content hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def expr_hash(expr: Expr) -> str:
    """Compute content hash of an expression (Appendix III wire format)."""
    return hashlib.sha256(_canonical_json(expr.to_json()).encode()).hexdigest()


def expr_to_json(expr: Expr) -> dict[str, Any]:
    """Convert expression to JSON wire format."""
    return expr.to_json()


def expr_from_json(data: dict[str, Any]) -> Expr:  # ruff: ignore[too-many-return-statements, too-many-branches, complex-structure] - parser with many cases
    """Parse expression from JSON wire format."""
    type_map = {
        "Var": Var,
        "Const": Const,
        "Not": Not,
        "And": And,
        "Or": Or,
        "Eq": Eq,
        "Ne": Ne,
        "Lt": Lt,
        "Le": Le,
        "Gt": Gt,
        "Ge": Ge,
        "In": In,
        "NotIn": NotIn,
        "HasKey": HasKey,
        "Call": Call,
        "Implies": Implies,
        "Add": Add,
        "Sub": Sub,
        "Mul": Mul,
        "Div": Div,
        "ForAll": ForAll,
        "Exists": Exists,
        "Mean": Mean,
        "Max": Max,
        "Min": Min,
        "Std": Std,
        "Diff": Diff,
        "Ratio": Ratio,
        "Template": Template,
        "Bind": Bind,
        "Eventually": Eventually,
        "Always": Always,
        "Monotonic": Monotonic,
    }
    cls = type_map.get(data["type"])
    if cls is None:
        raise ValueError(f"Unknown expression type: {data['type']}")

    if cls is Var:
        return Var(data["name"])
    if cls is Const:
        return Const(data["value"])
    if cls is Not:
        return Not(expr_from_json(data["expr"]))
    if cls is And:
        return And(expr_from_json(data["left"]), expr_from_json(data["right"]))
    if cls is Or:
        return Or(expr_from_json(data["left"]), expr_from_json(data["right"]))
    if cls in _BINARY_OPS:
        return cls(expr_from_json(data["left"]), expr_from_json(data["right"]))
    if cls in _ARITHMETIC_OPS:
        return cls(expr_from_json(data["left"]), expr_from_json(data["right"]))
    if cls is HasKey:
        return HasKey(expr_from_json(data["obj"]), expr_from_json(data["key"]))
    if cls is Call:
        return Call(data["func"], tuple(expr_from_json(arg) for arg in data["args"]))
    if cls is Implies:
        return Implies(expr_from_json(data["left"]), expr_from_json(data["right"]))
    if cls in _QUANTIFIERS:
        return cls(expr_from_json(data["filter"]), expr_from_json(data["body"]))
    if cls in _AGGREGATIONS:
        return cls(expr_from_json(data["expr"]), tuple(data.get("group_by", ())))
    if cls in _COMPARATIVE:
        return cls(expr_from_json(data["left"]), expr_from_json(data["right"]))
    if cls is Template:
        return Template(
            data["name"], tuple(data["params"]), expr_from_json(data["body"])
        )
    if cls is Bind:
        return Bind(
            data["template"],
            {k: expr_from_json(v) for k, v in data["bindings"].items()},
        )
    if cls is Monotonic:
        return Monotonic(expr_from_json(data["expr"]), data["direction"])
    if cls in _TRAJECTORY_OPS:
        return cls(expr_from_json(data["predicate"]), data.get("within"))

    raise ValueError(f"Unhandled expression type: {data['type']}")


_COORD_AXES = frozenset({
    "substrate",
    "geometry",
    "dynamics",
    "plasticity",
    "credit",
    "update",
})


class CoordinateContext:
    """Resolve variables from a bare coordinate.

    The single source of truth for coordinate-derived variables, shared by
    record evaluation and by schema availability (which must decide before
    anything has been measured).
    """

    def __init__(self, coordinate: Coordinate, task: str | None = None) -> None:
        self.coordinate = coordinate
        self.task = task

    def resolve_var(self, name: str) -> Any:  # ruff: ignore[too-many-return-statements] - expected for resolver
        """Resolve a coordinate axis or hyperparameter name."""
        if name in _COORD_AXES:
            return getattr(self.coordinate, name)

        if name.startswith("params."):
            return self.coordinate.params.get(name.split(".", 1)[1])

        if name in self.coordinate.params:
            return self.coordinate.params[name]

        if name == "task" and self.task is not None:
            return self.task

        return None


class EvaluationContext(CoordinateContext):
    """Context for evaluating expressions against a record."""

    def __init__(self, record: Record) -> None:
        self.record = record
        super().__init__(
            Coordinate(
                substrate=record.substrate,
                geometry=record.geometry,
                dynamics=record.dynamics,
                plasticity=record.plasticity,
                credit=record.credit,
                update=record.update,
                params=record.params,
            )
        )

    def resolve_var(self, name: str) -> Any:  # ruff: ignore[too-many-return-statements] - expected for resolver
        """Resolve a variable name to a value."""
        # Schedule fields
        if name.startswith("schedule."):
            field = name.split(".", 1)[1]
            return getattr(self.record.schedule, field, None)

        # Status fields
        if name.startswith("status."):
            field = name.split(".", 1)[1]
            return getattr(self.record.status, field, None)

        # Payload fields
        if name.startswith("payload."):
            key = name.split(".", 1)[1]
            return self.record.payload.get(key)

        # Provenance fields
        if name.startswith("provenance."):
            field = name.split(".", 1)[1]
            return getattr(self.record.provenance, field, None)

        # Baseline/ruler fields
        if name.startswith("baseline."):
            key = name.split(".", 1)[1]
            return self.record.payload.get(f"baseline_{key}")
        if name.startswith("ruler."):
            key = name.split(".", 1)[1]
            return self.record.payload.get(f"ruler_{key}")

        return super().resolve_var(name)


class CampaignContext:
    """Context for evaluating population-level expressions over multiple records.

    Provides quantifiers (ForAll, Exists), aggregations (Mean, Max, Min, Std),
    and comparative operations (Diff, Ratio) over a collection of records.
    """

    def __init__(self, records: list[Record]) -> None:
        self.records = records
        self._contexts = [EvaluationContext(r) for r in records]

    def filter_records(self, filter_expr: Expr) -> list[Record]:
        """Filter records by a predicate expression."""
        return [
            r
            for r, ctx in zip(self.records, self._contexts)
            if evaluate(filter_expr, ctx)
        ]

    def eval_forall(self, filter_expr: Expr, body_expr: Expr) -> bool:
        """Evaluate ForAll: body must hold for all records matching filter."""
        filtered = self.filter_records(filter_expr)
        if not filtered:
            return True  # Vacuous truth
        filtered_ctxs = [EvaluationContext(r) for r in filtered]
        return all(evaluate(body_expr, ctx) for ctx in filtered_ctxs)

    def eval_exists(self, filter_expr: Expr, body_expr: Expr) -> bool:
        """Evaluate Exists: body must hold for at least one record matching filter."""
        filtered = self.filter_records(filter_expr)
        if not filtered:
            return False
        filtered_ctxs = [EvaluationContext(r) for r in filtered]
        return any(evaluate(body_expr, ctx) for ctx in filtered_ctxs)

    def eval_aggregation(
        self, agg_type: str, expr: Expr, group_by: tuple[str, ...]
    ) -> float | dict[tuple, float]:
        """Evaluate aggregation (Mean, Max, Min, Std) with optional grouping."""
        if group_by:
            # Group records by the specified fields
            groups: dict[tuple, list[Record]] = {}
            for record in self.records:
                key = tuple(
                    EvaluationContext(record).resolve_var(field) for field in group_by
                )
                groups.setdefault(key, []).append(record)

            results = {}
            for key, group_records in groups.items():
                values = [
                    _eval_value(expr, EvaluationContext(r)) for r in group_records
                ]
                results[key] = self._compute_agg(agg_type, values)
            return results
        else:
            values = [_eval_value(expr, EvaluationContext(r)) for r in self.records]
            return self._compute_agg(agg_type, values)

    def _compute_agg(self, agg_type: str, values: list[Any]) -> float:  # ruff: ignore[too-many-return-statements]
        """Compute aggregation over a list of values."""
        if not values:
            return float("nan")
        numeric_values = [float(v) for v in values if isinstance(v, (int, float))]
        if not numeric_values:
            return float("nan")
        if agg_type == "Mean":
            return sum(numeric_values) / len(numeric_values)
        if agg_type == "Max":
            return max(numeric_values)
        if agg_type == "Min":
            return min(numeric_values)
        if agg_type == "Std":
            if len(numeric_values) < 2:
                return 0.0
            mean = sum(numeric_values) / len(numeric_values)
            variance = sum((x - mean) ** 2 for x in numeric_values) / (
                len(numeric_values) - 1
            )
            return variance**0.5
        raise ValueError(f"Unknown aggregation type: {agg_type}")

    def eval_diff(self, left: Expr, right: Expr) -> float | dict[tuple, float]:
        """Evaluate difference between two expressions."""
        left_vals = [_eval_value(left, EvaluationContext(r)) for r in self.records]
        right_vals = [_eval_value(right, EvaluationContext(r)) for r in self.records]
        return [lv - rv for lv, rv in zip(left_vals, right_vals)]

    def eval_ratio(self, left: Expr, right: Expr) -> float | dict[tuple, float]:
        """Evaluate ratio between two expressions."""
        left_vals = [_eval_value(left, EvaluationContext(r)) for r in self.records]
        right_vals = [_eval_value(right, EvaluationContext(r)) for r in self.records]
        return [
            lv / rv if rv != 0 else float("inf") for lv, rv in zip(left_vals, right_vals)
        ]

    def eval_template_bind(
        self,
        template_name: str,
        _bindings: dict[str, Expr],
        templates: dict[str, Template],
    ) -> Any:
        """Bind a template with parameter values."""
        template = templates.get(template_name)
        if template is None:
            raise ValueError(f"Template not found: {template_name}")
        # Substitute parameters in the template body
        # This is a simplified implementation - a full implementation would
        # substitute Var nodes matching parameter names
        return template

    def eval_eventually(self, predicate: Expr, within: int | None) -> bool:
        """Evaluate Eventually: predicate holds at some step in trajectory."""
        # Requires trajectory data in payload
        for record in self.records:
            trajectory = record.payload.get("trajectory")
            if not trajectory:
                continue
            steps = trajectory[:within] if within else trajectory
            for _step in steps:
                # Would need a trajectory-specific evaluation context
                # For now, simplified check
                ctx = EvaluationContext(record)
                if evaluate(predicate, ctx):
                    return True
        return False

    def eval_always(self, predicate: Expr, within: int | None) -> bool:
        """Evaluate Always: predicate holds at all steps in trajectory."""
        for record in self.records:
            trajectory = record.payload.get("trajectory")
            if not trajectory:
                continue
            steps = trajectory[:within] if within else trajectory
            for _step in steps:
                ctx = EvaluationContext(record)
                if not evaluate(predicate, ctx):
                    return False
        return bool(self.records)

    def eval_monotonic(self, expr: Expr, direction: str) -> bool:
        """Evaluate Monotonic: values strictly increase/decrease."""
        from itertools import pairwise

        for record in self.records:
            trajectory = record.payload.get("trajectory")
            if not trajectory:
                continue
            values = []
            for _step in trajectory:
                # Would need trajectory-specific context
                ctx = EvaluationContext(record)
                val = _eval_value(expr, ctx)
                if isinstance(val, (int, float)):
                    values.append(float(val))
            if len(values) < 2:
                continue
            if direction == "increase" and not all(
                v2 > v1 for v1, v2 in pairwise(values)
            ):
                return False
            if direction == "decrease" and not all(
                v2 < v1 for v1, v2 in pairwise(values)
            ):
                return False
        return True


def _eval_binary(  # ruff: ignore[complex-structure, too-many-return-statements] - binary op dispatcher
    left: Expr, right: Expr, ctx: CoordinateContext, op: str
) -> bool:
    """Evaluate binary comparison."""
    left_val = _eval_value(left, ctx)
    right_val = _eval_value(right, ctx)
    match op:
        case "eq":
            return left_val == right_val
        case "ne":
            return left_val != right_val
        case "lt":
            return left_val < right_val
        case "le":
            return left_val <= right_val
        case "gt":
            return left_val > right_val
        case "ge":
            return left_val >= right_val
        case "in":
            if isinstance(right_val, (list, tuple, set, frozenset, dict, str)):
                return left_val in right_val
            return False
        case "not_in":
            if isinstance(right_val, (list, tuple, set, frozenset, dict, str)):
                return left_val not in right_val
            return True
        case _:
            raise ValueError(f"Unknown binary op: {op}")


def _eval_value(  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches, too-many-locals, too-many-statements] - match/case evaluator
    expr: Expr, ctx: CoordinateContext | CampaignContext
) -> Any:
    """Evaluate an expression to its actual value (not coerced to bool)."""
    # CampaignContext-only expressions
    if isinstance(ctx, CampaignContext):
        match expr:
            case ForAll(filter_expr, body_expr):
                return ctx.eval_forall(filter_expr, body_expr)
            case Exists(filter_expr, body_expr):
                return ctx.eval_exists(filter_expr, body_expr)
            case Mean(expr, group_by):
                return ctx.eval_aggregation("Mean", expr, group_by)
            case Max(expr, group_by):
                return ctx.eval_aggregation("Max", expr, group_by)
            case Min(expr, group_by):
                return ctx.eval_aggregation("Min", expr, group_by)
            case Std(expr, group_by):
                return ctx.eval_aggregation("Std", expr, group_by)
            case Diff(left, right):
                return ctx.eval_diff(left, right)
            case Ratio(left, right):
                return ctx.eval_ratio(left, right)
            case Bind(template, _bindings):
                # Templates need a registry - return template name for now
                return template
            case Eventually(predicate, within):
                return ctx.eval_eventually(predicate, within)
            case Always(predicate, within):
                return ctx.eval_always(predicate, within)
            case Monotonic(expr, direction):
                return ctx.eval_monotonic(expr, direction)
            case Template(_name, _params, _body):
                # Template definition - return the template object
                return expr

    # CoordinateContext expressions
    match expr:
        case Var(name):
            return ctx.resolve_var(name)

        case Const(value):
            return value

        case Not(expr):
            return not _eval_value(expr, ctx)

        case And(left, right):
            return _eval_value(left, ctx) and _eval_value(right, ctx)

        case Or(left, right):
            return _eval_value(left, ctx) or _eval_value(right, ctx)

        case Eq(left, right):
            return _eval_value(left, ctx) == _eval_value(right, ctx)

        case Ne(left, right):
            return _eval_value(left, ctx) != _eval_value(right, ctx)

        case Lt(left, right):
            return _eval_value(left, ctx) < _eval_value(right, ctx)

        case Le(left, right):
            return _eval_value(left, ctx) <= _eval_value(right, ctx)

        case Gt(left, right):
            return _eval_value(left, ctx) > _eval_value(right, ctx)

        case Ge(left, right):
            return _eval_value(left, ctx) >= _eval_value(right, ctx)

        case In(left, right):
            left_val = _eval_value(left, ctx)
            right_val = _eval_value(right, ctx)
            if isinstance(right_val, (list, tuple, set, frozenset, dict, str)):
                return left_val in right_val
            return False

        case NotIn(left, right):
            left_val = _eval_value(left, ctx)
            right_val = _eval_value(right, ctx)
            if isinstance(right_val, (list, tuple, set, frozenset, dict, str)):
                return left_val not in right_val
            return True

        case HasKey(obj, key):
            obj_val = _eval_value(obj, ctx)
            key_val = _eval_value(key, ctx)
            if isinstance(obj_val, dict):
                return key_val in obj_val
            if hasattr(obj_val, "__contains__"):
                try:
                    return key_val in obj_val
                except TypeError:
                    return False
            return False

        case Call(func, args):
            arg_values = [_eval_value(arg, ctx) for arg in args]
            # Built-in functions - return actual values
            match func:
                case "len":
                    if len(arg_values) == 1 and hasattr(arg_values[0], "__len__"):
                        return len(arg_values[0])
                    return 0
                case "all":
                    return all(arg_values)
                case "any":
                    return any(arg_values)
                case "min":
                    return min(arg_values) if arg_values else None
                case "max":
                    return max(arg_values) if arg_values else None
                case _:
                    # Unknown function - return None
                    return None

        case Add(left, right):
            left_val = _eval_value(left, ctx)
            right_val = _eval_value(right, ctx)
            return left_val + right_val

        case Sub(left, right):
            left_val = _eval_value(left, ctx)
            right_val = _eval_value(right, ctx)
            return left_val - right_val

        case Mul(left, right):
            left_val = _eval_value(left, ctx)
            right_val = _eval_value(right, ctx)
            return left_val * right_val

        case Div(left, right):
            left_val = _eval_value(left, ctx)
            right_val = _eval_value(right, ctx)
            if right_val == 0:
                return float("inf")
            return left_val / right_val

        case Implies(left, right):
            left_val = _eval_value(left, ctx)
            right_val = _eval_value(right, ctx)
            return (not bool(left_val)) or bool(right_val)

        case _:
            raise ValueError(f"Unknown expression type: {type(expr)}")


def evaluate(expr: Expr, ctx: CoordinateContext | CampaignContext) -> bool:  # ruff: ignore[complex-structure,too-many-return-statements,too-many-branches] - match/case evaluator
    """Evaluate an expression as a predicate (coerced to bool)."""
    return bool(_eval_value(expr, ctx))


def expr_from_string(s: str) -> Expr:
    """Parse a simple expression string into an Expr.

    Supports basic forms: "var_name", "var_name == value", "var_name in [a, b, c]",
    "var_name > value", "var_name < value", etc.
    """
    # Simple parser for common cases
    s = s.strip()

    # Check for binary operators
    for op_str, op_func in [
        (" == ", eq),
        (" != ", ne),
        (" >= ", ge),
        (" <= ", le),
        (" > ", gt),
        (" < ", lt),
        (" in ", in_),
        (" not in ", not_in),
    ]:
        if op_str in s:
            left, right = s.split(op_str, 1)
            left = left.strip()
            right = right.strip()
            # Try to parse right as a value
            try:
                # Try to evaluate as Python literal
                import ast

                right_val = ast.literal_eval(right)
            except ValueError, SyntaxError:
                right_val = right
            return op_func(var(left), const(right_val))

    # Default: just a variable reference
    return var(s)


# Convenience builders
def var(name: str) -> Var:
    return Var(name)


def const(value: Any) -> Const:
    return Const(value)


def not_(expr: Expr) -> Not:
    return Not(expr)


def and_(*exprs: Expr) -> Expr:
    if not exprs:
        return const(True)
    result = exprs[0]
    for expr in exprs[1:]:
        result = And(result, expr)
    return result


def or_(*exprs: Expr) -> Expr:
    if not exprs:
        return const(False)
    result = exprs[0]
    for expr in exprs[1:]:
        result = Or(result, expr)
    return result


def eq(left: Expr, right: Expr) -> Eq:
    return Eq(left, right)


def ne(left: Expr, right: Expr) -> Ne:
    return Ne(left, right)


def lt(left: Expr, right: Expr) -> Lt:
    return Lt(left, right)


def le(left: Expr, right: Expr) -> Le:
    return Le(left, right)


def gt(left: Expr, right: Expr) -> Gt:
    return Gt(left, right)


def ge(left: Expr, right: Expr) -> Ge:
    return Ge(left, right)


def in_(left: Expr, right: Expr) -> In:
    return In(left, right)


def not_in(left: Expr, right: Expr) -> NotIn:
    return NotIn(left, right)


def has_key(obj: Expr, key: Expr) -> HasKey:
    return HasKey(obj, key)


def call(func: str, *args: Expr) -> Call:
    return Call(func, args)


def implies(left: Expr, right: Expr) -> Implies:
    return Implies(left, right)


def add(left: Expr, right: Expr) -> Add:
    return Add(left, right)


def sub(left: Expr, right: Expr) -> Sub:
    return Sub(left, right)


def mul(left: Expr, right: Expr) -> Mul:
    return Mul(left, right)


def div(left: Expr, right: Expr) -> Div:
    return Div(left, right)


# Phase 1: Quantifiers and Aggregations
def forall(filter_expr: Expr, body_expr: Expr) -> ForAll:
    return ForAll(filter_expr, body_expr)


def exists(filter_expr: Expr, body_expr: Expr) -> Exists:
    return Exists(filter_expr, body_expr)


def mean(expr: Expr, group_by: tuple[str, ...] = ()) -> Mean:
    return Mean(expr, group_by)


def max_(expr: Expr, group_by: tuple[str, ...] = ()) -> Max:
    return Max(expr, group_by)


def min_(expr: Expr, group_by: tuple[str, ...] = ()) -> Min:
    return Min(expr, group_by)


def std(expr: Expr, group_by: tuple[str, ...] = ()) -> Std:
    return Std(expr, group_by)


def diff(left: Expr, right: Expr) -> Diff:
    return Diff(left, right)


def ratio(left: Expr, right: Expr) -> Ratio:
    return Ratio(left, right)


# Phase 2: Hypothesis Templates
def template(name: str, params: tuple[str, ...], body: Expr) -> Template:
    return Template(name, params, body)


def bind(template: str, bindings: dict[str, Expr]) -> Bind:
    return Bind(template, bindings)


# Phase 3: Trajectory Operators
def eventually(predicate: Expr, within: int | None = None) -> Eventually:
    return Eventually(predicate, within)


def always(predicate: Expr, within: int | None = None) -> Always:
    return Always(predicate, within)


def monotonic(expr: Expr, direction: str = "increase") -> Monotonic:
    return Monotonic(expr, direction)


__all__ = [
    "Add",
    "Always",
    "Bind",
    "Call",
    "CampaignContext",
    "Const",
    "CoordinateContext",
    "Diff",
    "Div",
    "Eq",
    "EvaluationContext",
    "Eventually",
    "Exists",
    "Expr",
    "ForAll",
    "Ge",
    "Gt",
    "HasKey",
    "Implies",
    "In",
    "Le",
    "Lt",
    "Max",
    "Mean",
    "Min",
    "Monotonic",
    "Mul",
    "Ne",
    "Not",
    "NotIn",
    "Or",
    "Ratio",
    "Std",
    "Sub",
    "Template",
    "Var",
    "add",
    "always",
    "and_",
    "bind",
    "call",
    "const",
    "diff",
    "div",
    "eq",
    "evaluate",
    "eventually",
    "exists",
    "expr_from_json",
    "expr_from_string",
    "expr_hash",
    "expr_to_json",
    "forall",
    "ge",
    "gt",
    "has_key",
    "implies",
    "in_",
    "le",
    "lt",
    "max_",
    "mean",
    "min_",
    "monotonic",
    "mul",
    "ne",
    "not_",
    "not_in",
    "or_",
    "ratio",
    "std",
    "sub",
    "template",
    "var",
]
