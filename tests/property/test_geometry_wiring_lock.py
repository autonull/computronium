"""Geometry wiring lockstep lock (the dynamics-lock analogue for the G axis).

Every future Geometry primitive must hit every export surface in
lockstep — the NcaGeometry landing (TODO.ntm_nca.md §10 item 1) needed
the dispatch chain, two __all__ lists, _LAZY, and the root
TYPE_CHECKING block touched together. This lock makes skipping a
surface impossible:

1. every ``GeometryConfig`` factory classmethod's ``topology_type``
   dispatches through ``geometry_from_config`` and round-trips its
   config exactly;
2. every alias literal in the dispatch body resolves to a geometry
   class defined in ``geometry.py``;
3. every geometry class defined in ``geometry.py`` appears in the
   ontology ``__all__``, root ``__all__``, root ``_LAZY``, and the root
   ``TYPE_CHECKING`` import block.
"""

import dataclasses
import inspect
from pathlib import Path

import computronium.ontology.geometry as geometry_module
from computronium import _LAZY
from computronium.ontology.geometry import (
    GeometryConfig,
    geometry_from_config,
)

ROOT_INIT = Path("computronium") / "__init__.py"
ONTOLOGY_INIT = Path("computronium") / "ontology" / "__init__.py"


def _geometry_classes() -> set[str]:
    return {
        name
        for name, member in vars(geometry_module).items()
        if inspect.isclass(member)
        and name.endswith("Geometry")
        and name != "Geometry"  # the Protocol, not an implementation
        and member.__module__ == geometry_module.__name__
    }


def _config_classmethods() -> dict[str, str]:
    """Map factory-classmethod name -> topology_type of the returned config."""
    found: dict[str, str] = {}
    for name, member in vars(GeometryConfig).items():
        if name.startswith("_") or not isinstance(member, classmethod):
            continue
        try:
            config = getattr(GeometryConfig, name)()
        except TypeError:
            continue  # classmethod with required args is not a no-arg factory
        if isinstance(config, GeometryConfig):
            found[name] = config.topology_type
    return found


def test_config_classmethods_dispatch_and_round_trip() -> None:
    for name, topology_type in _config_classmethods().items():
        config = GeometryConfig(**dataclasses.asdict(getattr(GeometryConfig, name)()))
        geometry = geometry_from_config(config)
        assert geometry.config.topology_type == topology_type, name
        assert geometry.config == config, name


def _dispatch_aliases() -> set[str]:
    """Alias literals the dispatcher actually accepts.

    Read from the dispatch tables rather than by scanning source text: the
    dispatcher is table-driven, so a regex over its body found nothing and
    the lock silently degraded to "covers 0 classes".
    """
    return set(geometry_module._GEOMETRY_FACTORIES) | set(
        geometry_module._GEOMETRY_DISPATCH
    )


def test_dispatch_aliases_resolve_to_geometry_classes() -> None:
    aliases = _dispatch_aliases()
    classes = _geometry_classes()
    resolved: set[str] = set()
    for alias in aliases:
        config = GeometryConfig(
            input_dim=4,
            output_dim=4,
            hidden_dims=(8,),
            num_layers=1,
            topology_type=alias,
            connectivity={"edge_index": [[0, 1], [1, 0]]},
            recurrent_weight=None,
        )
        resolved.add(type(geometry_from_config(config)).__name__)
    assert aliases, "dispatch tables are empty"
    assert resolved <= classes, (
        f"dispatch aliases resolve outside geometry.py: {resolved - classes}"
    )
    assert len(resolved) == len(classes), (
        f"dispatch covers {len(resolved)} classes but geometry.py defines "
        f"{len(classes)}: {classes - resolved}"
    )


def test_geometry_classes_are_exported_everywhere() -> None:
    from computronium import __all__

    ontology_all = ONTOLOGY_INIT.read_text(encoding="utf-8")
    root_source = ROOT_INIT.read_text(encoding="utf-8")
    type_checking_block = root_source.split("if TYPE_CHECKING:", 1)[1]
    for name in sorted(_geometry_classes()):
        assert f'"{name}"' in ontology_all, f"{name} missing from ontology __all__"
        assert name in __all__, f"{name} missing from root __all__"
        assert name in _LAZY, f"{name} missing from root _LAZY"
        assert _LAZY[name][1] == name
        assert name in type_checking_block, (
            f"{name} missing from the root TYPE_CHECKING import block"
        )
