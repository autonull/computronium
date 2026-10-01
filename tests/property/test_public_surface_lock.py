"""The package's declared public surface, checked as a population.

``computronium/__init__`` calls :func:`assert_public_surface` at import time,
so importing the package here has already run the real check -- if it failed,
this file would not be collected. What this adds is the two things an
import-time check cannot give: that the *population* is what we think it is
(an empty documented set would make the check vacuous), and that the check
still reports a broken surface rather than passing by construction.

The population is the README's documented entry points plus the root's
``__all__``/``_LAZY`` pair, which is what §0.2 item 1 put under guard.
"""

from __future__ import annotations

import pytest

import computronium
from computronium import _surface

# The README names these three ways: backticked source paths, ``python -m``
# invocations, and dotted references. Each has to be in the population, or the
# import-time check is guarding less than this round put it there to guard.
EXPECTED_PATHS = {
    "computronium/experiment/execution/policy.py",
    "computronium/ontology/substrate/spec.py",
}
EXPECTED_DOTTED = {
    "computronium.experiment",
    "computronium.models.native",
    "computronium.verification",
}


def test_the_documented_population_is_the_one_we_think_it_is() -> None:
    paths, dotted = _surface.documented_entry_points()

    assert set(paths) >= EXPECTED_PATHS
    assert set(dotted) >= EXPECTED_DOTTED
    assert len(paths) + len(dotted) >= 5, (
        "the documented population shrank: the guard is now covering less than "
        "the README names, which is the vacuous-lock failure mode"
    )


def test_every_documented_module_exists() -> None:
    paths, dotted = _surface.documented_entry_points()
    root = _surface._ROOT.parent

    missing = [p for p in paths if not (root / p).is_file()]
    missing += [m for m in dotted if _surface.module_path(m) is None]
    assert not missing, f"README documents modules that do not exist: {missing}"


def test_the_real_surface_has_no_problems() -> None:
    problems = _surface.surface_problems(
        computronium.__all__, computronium._LAZY, {"__version__"}
    )

    assert problems == []


def test_an_undefined_lazy_target_is_reported() -> None:
    problems = _surface.surface_problems(
        ["Ghost"],
        {"Ghost": ("computronium.core.presets", "NotDefinedAnywhere")},
        set(),
    )

    assert problems == [
        "Ghost maps to computronium.core.presets.NotDefinedAnywhere, "
        "which is not defined"
    ]


def test_an_unmapped_export_is_reported() -> None:
    problems = _surface.surface_problems(
        [*computronium.__all__, "Ghost"], computronium._LAZY, {"__version__"}
    )

    assert "Ghost is in __all__ but nothing binds it" in problems


def test_a_lazy_target_module_that_does_not_exist_is_reported() -> None:
    problems = _surface.surface_problems(
        ["Ghost"], {"Ghost": ("computronium.core.no_such_module", "Thing")}, set()
    )

    assert problems == [
        "Ghost maps to computronium.core.no_such_module, which does not exist"
    ]


@pytest.mark.parametrize(
    ("source", "bound"),
    [
        ("type Alias = int\n", "Alias"),
        ("def f() -> None: ...\n", "f"),
        ("async def g() -> None: ...\n", "g"),
        ("class C: ...\n", "C"),
        ("NAME = 1\n", "NAME"),
        ("annotated: int = 1\n", "annotated"),
        ("from os import path\n", "path"),
        ("from os import path as p\n", "p"),
        (
            "try:\n    from json import JSONDecoder\nexcept ImportError:\n    pass\n",
            "JSONDecoder",
        ),
    ],
)
def test_the_name_scan_sees_every_way_a_module_binds(
    tmp_path, source: str, bound: str
) -> None:
    """A name the scan cannot see is a name the import-time guard cannot check.

    Every binding form the tree actually uses has an entry here, including the
    ``try``-guarded re-export and the PEP 695 ``type`` alias -- the alias was
    missing when the guard first ran, and reported a false alarm on a live
    import.
    """
    path = tmp_path / "probe.py"
    path.write_text(source)

    assert bound in _surface.bound_names(path)
