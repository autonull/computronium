# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""No docstring."""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=True,
        factory_name="create_ternary_eqprop_mlp",
    )
)
