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


_BINARY_OPS = frozenset({Eq, Ne, Lt, Le, Gt, Ge, In, NotIn})


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for content hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def expr_hash(expr: Expr) -> str:
    """Compute content hash of an expression (Appendix III wire format)."""
    return hashlib.sha256(_canonical_json(expr.to_json()).encode()).hexdigest()


def expr_to_json(expr: Expr) -> dict[str, Any]:
    """Convert expression to JSON wire format."""
    return expr.to_json()


def expr_from_json(data: dict[str, Any]) -> Expr:  # noqa: PLR0911 - parser with many cases
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
    if cls is HasKey:
        return HasKey(expr_from_json(data["obj"]), expr_from_json(data["key"]))
    if cls is Call:
        return Call(data["func"], tuple(expr_from_json(arg) for arg in data["args"]))

    raise ValueError(f"Unhandled expression type: {data['type']}")


_COORD_AXES = frozenset({
    "substrate",
    "geometry",
    "dynamics",
    "plasticity",
    "credit",
    "update",
})


class EvaluationContext:
    """Context for evaluating expressions against a record."""

    def __init__(self, record: Record) -> None:
        self.record = record
        self.coordinate = Coordinate(
            substrate=record.substrate,
            geometry=record.geometry,
            dynamics=record.dynamics,
            plasticity=record.plasticity,
            credit=record.credit,
            update=record.update,
            params=record.params,
        )

    def resolve_var(self, name: str) -> Any:  # noqa: PLR0911 - expected for resolver
        """Resolve a variable name to a value."""
        # Schedule fields
        if name.startswith("schedule."):
            field = name.split(".", 1)[1]
            return getattr(self.record.schedule, field, None)

        # Coordinate structural axes
        if name in _COORD_AXES:
            return getattr(self.coordinate, name)

        # Params (hyperparameters)
        if name.startswith("params."):
            key = name.split(".", 1)[1]
            return self.coordinate.params.get(key)

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

        # Direct coordinate params
        if name in self.coordinate.params:
            return self.coordinate.params[name]

        return None


def _eval_binary(  # noqa: C901,PLR0911 - binary op dispatcher
    left: Expr, right: Expr, ctx: EvaluationContext, op: str
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


def _eval_value(expr: Expr, ctx: EvaluationContext) -> Any:  # noqa: C901,PLR0911,PLR0912 - match/case evaluator
    """Evaluate an expression to its actual value (not coerced to bool)."""
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

        case _:
            raise ValueError(f"Unknown expression type: {type(expr)}")


def evaluate(expr: Expr, ctx: EvaluationContext) -> bool:  # noqa: C901,PLR0911,PLR0912 - match/case evaluator
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


__all__ = [
    "Call",
    "Const",
    "Eq",
    "EvaluationContext",
    "Expr",
    "Ge",
    "Gt",
    "HasKey",
    "In",
    "Le",
    "Lt",
    "Ne",
    "Not",
    "NotIn",
    "Or",
    "Var",
    "and_",
    "call",
    "const",
    "eq",
    "evaluate",
    "expr_from_json",
    "expr_from_string",
    "expr_hash",
    "expr_to_json",
    "ge",
    "gt",
    "has_key",
    "in_",
    "le",
    "lt",
    "ne",
    "not_",
    "not_in",
    "or_",
    "var",
]
