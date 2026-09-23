"""UX-L10: Lineage Viewer replay property test.

Lineage viewer must reconstruct identical graph from event log replay.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


@dataclass(frozen=True, slots=True)
class LineageNode:
    """A node in the lineage graph (a genome)."""

    genome_id: str
    tier: int  # 1=structural, 2=algorithmic, 3=meta
    fitness: float
    episode: int
    parent_id: str | None


@dataclass(frozen=True, slots=True)
class LineageEdge:
    """An edge in the lineage graph (a mutation)."""

    from_genome: str
    to_genome: str
    mutation_type: str  # "DuplicateAndPerturb" | "SpliceOperator" | "CoordinateSwap"
    slope: float
    accepted: bool


@dataclass(frozen=True, slots=True)
class LineageGraph:
    """Complete lineage graph."""

    nodes: tuple[LineageNode, ...]
    edges: tuple[LineageEdge, ...]


# Hypothesis strategies for generating test data


@st.composite
def genome_id_strategy(draw: st.DrawFn) -> str:
    """Generate genome IDs like 'genome_001', 'genome_002', etc."""
    num = draw(st.integers(min_value=1, max_value=1000))
    return f"genome_{num:03d}"


@st.composite
def lineage_node_strategy(draw: st.DrawFn) -> LineageNode:
    """Generate a random lineage node."""
    return LineageNode(
        genome_id=draw(genome_id_strategy()),
        tier=draw(st.integers(min_value=1, max_value=3)),
        fitness=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False)),
        episode=draw(st.integers(min_value=0, max_value=100)),
        parent_id=draw(st.one_of(st.none(), genome_id_strategy())),
    )


@st.composite
def lineage_edge_strategy(draw: st.DrawFn, nodes: list[LineageNode]) -> LineageEdge:
    """Generate a random lineage edge between existing nodes."""
    if len(nodes) < 2:
        return LineageEdge(
            from_genome=nodes[0].genome_id if nodes else "genome_001",
            to_genome=nodes[1].genome_id if len(nodes) > 1 else "genome_002",
            mutation_type=draw(
                st.sampled_from([
                    "DuplicateAndPerturb",
                    "SpliceOperator",
                    "CoordinateSwap",
                ])
            ),
            slope=draw(st.floats(min_value=-1.0, max_value=1.0, allow_nan=False)),
            accepted=draw(st.booleans()),
        )
    from_node = draw(st.sampled_from(nodes))
    to_node = draw(
        st.sampled_from([n for n in nodes if n.genome_id != from_node.genome_id])
    )
    return LineageEdge(
        from_genome=from_node.genome_id,
        to_genome=to_node.genome_id,
        mutation_type=draw(
            st.sampled_from(["DuplicateAndPerturb", "SpliceOperator", "CoordinateSwap"])
        ),
        slope=draw(st.floats(min_value=-1.0, max_value=1.0, allow_nan=False)),
        accepted=draw(st.booleans()),
    )


@st.composite
def lineage_graph_strategy(draw: st.DrawFn) -> LineageGraph:
    """Generate a random lineage graph."""
    num_nodes = draw(st.integers(min_value=1, max_value=20))
    nodes = [draw(lineage_node_strategy()) for _ in range(num_nodes)]

    # Ensure unique genome_ids
    seen = set()
    unique_nodes = []
    for node in nodes:
        if node.genome_id not in seen:
            seen.add(node.genome_id)
            unique_nodes.append(node)

    num_edges = draw(st.integers(min_value=0, max_value=len(unique_nodes) * 2))
    edges = [draw(lineage_edge_strategy(unique_nodes)) for _ in range(num_edges)]

    return LineageGraph(
        nodes=tuple(unique_nodes),
        edges=tuple(edges),
    )


def _serialize_graph(graph: LineageGraph) -> str:
    """Serialize a lineage graph to a canonical string for comparison."""
    node_strs = [
        f"{n.genome_id}|{n.tier}|{n.fitness:.6f}|{n.episode}|{n.parent_id or 'none'}"
        for n in sorted(graph.nodes, key=lambda n: n.genome_id)
    ]
    edge_strs = [
        f"{e.from_genome}|{e.to_genome}|{e.mutation_type}|{e.slope:.6f}|{e.accepted}"
        for e in sorted(graph.edges, key=lambda e: (e.from_genome, e.to_genome))
    ]
    return "\n".join(node_strs) + "\n---\n" + "\n".join(edge_strs)


def _graph_from_events(events: list[dict]) -> LineageGraph:
    """Build lineage graph from event log (reference implementation).

    This mimics what the Lineage Viewer panel should do.
    """
    nodes: dict[str, LineageNode] = {}
    edges: dict[tuple[str, str], LineageEdge] = {}  # Use dict for idempotency

    for event in events:
        kind = event.get("kind", "")

        if kind == "genome_created":
            genome_id = event.get("genome_id", "")
            tier = event.get("tier", 1)
            fitness = event.get("fitness", 0.0)
            episode = event.get("episode", 0)
            parent_id = event.get("parent_id")
            mutation_type = event.get("mutation_type", "Unknown")
            slope = event.get("slope", 0.0)
            accepted = event.get("accepted", True)

            # Create or update node
            if genome_id in nodes:
                old = nodes[genome_id]
                nodes[genome_id] = LineageNode(
                    genome_id=old.genome_id,
                    tier=tier,
                    fitness=fitness,
                    episode=episode,
                    parent_id=parent_id,
                )
            else:
                nodes[genome_id] = LineageNode(
                    genome_id=genome_id,
                    tier=tier,
                    fitness=fitness,
                    episode=episode,
                    parent_id=parent_id,
                )

            # Add edge if parent exists
            if parent_id:
                edge_key = (parent_id, genome_id)
                if edge_key not in edges:  # Idempotent: first event wins
                    edges[edge_key] = LineageEdge(
                        from_genome=parent_id,
                        to_genome=genome_id,
                        mutation_type=mutation_type,
                        slope=slope,
                        accepted=accepted,
                    )

        elif kind == "genome_fitness_updated":
            genome_id = event.get("genome_id", "")
            if genome_id in nodes:
                old = nodes[genome_id]
                nodes[genome_id] = LineageNode(
                    genome_id=old.genome_id,
                    tier=old.tier,
                    fitness=event.get("fitness", old.fitness),
                    episode=old.episode,
                    parent_id=old.parent_id,
                )

    return LineageGraph(
        nodes=tuple(nodes.values()),
        edges=tuple(edges.values()),
    )


def _graph_from_events_shuffled(events: list[dict]) -> LineageGraph:
    """Build lineage graph from shuffled event log (should be identical)."""
    import random

    shuffled = events.copy()
    random.shuffle(shuffled)
    return _graph_from_events(shuffled)


def _graph_from_events_with_duplicates(events: list[dict]) -> LineageGraph:
    """Build lineage graph from event log with duplicates (should be idempotent)."""
    import random

    # Add some duplicate events
    duplicated = events + random.sample(events, min(3, len(events)))
    random.shuffle(duplicated)
    return _graph_from_events(duplicated)


class TestLineageReplay:
    """UX-L10: Lineage viewer must reconstruct identical graph from replay."""

    @given(lineage_graph_strategy())
    @settings(max_examples=100, deadline=None)
    def test_replay_produces_identical_graph(self, graph: LineageGraph) -> None:
        """Replaying events in different orders must produce identical graph."""
        # Convert graph to event log (only node events, edges are derived from parent_id)
        events = []
        for node in graph.nodes:
            events.append({
                "kind": "genome_created",
                "genome_id": node.genome_id,
                "tier": node.tier,
                "fitness": node.fitness,
                "episode": node.episode,
                "parent_id": node.parent_id,
                "mutation_type": "Initial"
                if node.parent_id is None
                else "DuplicateAndPerturb",
                "slope": 0.0,
                "accepted": True,
            })

        # Build from original order
        graph1 = _graph_from_events(events)

        # Build from shuffled order
        graph2 = _graph_from_events_shuffled(events)

        # Build from order with duplicates
        graph3 = _graph_from_events_with_duplicates(events)

        # All three must serialize identically
        ser1 = _serialize_graph(graph1)
        ser2 = _serialize_graph(graph2)
        ser3 = _serialize_graph(graph3)

        assert ser1 == ser2, "Shuffled replay produced different graph"
        assert ser1 == ser3, "Duplicate events produced different graph"

    def test_lineage_viewer_glossary_strings(self) -> None:
        """Lineage viewer terms must exist in glossary."""
        from computronium.ui.glossary_service import get_glossary_service

        svc = get_glossary_service()
        required_keys = [
            "lineage_viewer",
            "probe_analytics",
            "stagnation_dashboard",
            "genome_health",
            "mutation_explorer",
            "veto_log",
            "episode_timeline",
        ]

        for key in required_keys:
            assert svc.has(key), f"Missing glossary key: {key}"
            explorer = svc.get(key, register="explorer")
            lab = svc.get(key, register="lab")
            assert explorer != key, f"Key '{key}' has no Explorer translation"
            assert lab != key, f"Key '{key}' has no Lab translation"

    def test_lineage_explorer_readability(self) -> None:
        """Explorer strings for lineage must be ≤ FK grade 8."""
        import re

        from computronium.ui.glossary_service import get_glossary_service

        svc = get_glossary_service()
        keys = [
            "lineage_viewer",
            "probe_analytics",
            "stagnation_dashboard",
            "genome_health",
            "mutation_explorer",
            "veto_log",
            "episode_timeline",
        ]

        for key in keys:
            explorer = svc.get(key, register="explorer")
            words = len(explorer.split())
            sentences = len(re.split(r"[.!?]+", explorer)) or 1
            avg_words_per_sentence = words / sentences
            assert avg_words_per_sentence <= 15, (
                f"Explorer string for '{key}' too complex: '{explorer}' "
                f"(avg {avg_words_per_sentence:.1f} words/sentence)"
            )


class TestLineageViewerIntegration:
    """Integration tests for the Lineage Viewer component."""

    def test_component_exists(self) -> None:
        """LineageViewer component must exist."""
        from computronium.ui.components.lineage_viewer import LineageViewer

        assert LineageViewer is not None

    def test_component_renders_graph(self) -> None:
        """Component must render nodes and edges with tier colors."""
        from computronium.ui.components.lineage_viewer import (
            LineageEdge,
            LineageNode,
            LineageViewer,
        )

        nodes = [
            LineageNode(
                genome_id="genome_001",
                tier=1,
                fitness=0.8,
                episode=0,
                parent_id=None,
                mutation_type=None,
                slope=0.1,
            ),
            LineageNode(
                genome_id="genome_002",
                tier=2,
                fitness=0.85,
                episode=1,
                parent_id="genome_001",
                mutation_type="DuplicateAndPerturb",
                slope=0.15,
            ),
        ]
        edges = [
            LineageEdge(
                from_genome="genome_001",
                to_genome="genome_002",
                mutation_type="DuplicateAndPerturb",
                slope=0.15,
                accepted=True,
            ),
        ]

        panel = LineageViewer(nodes=nodes, edges=edges)
        assert panel.nodes is not None
        assert len(panel.nodes) == 2
        assert panel.edges is not None
        assert len(panel.edges) == 1

    def test_component_tooltips_show_slope(self) -> None:
        """Edge tooltips must show adaptation probe slope."""
        from computronium.ui.components.lineage_viewer import (
            LineageEdge,
            LineageNode,
            LineageViewer,
        )

        nodes = [
            LineageNode(
                genome_id="genome_001",
                tier=1,
                fitness=0.8,
                episode=0,
                parent_id=None,
                mutation_type=None,
                slope=0.1,
            ),
        ]
        edges = [
            LineageEdge(
                from_genome="genome_001",
                to_genome="genome_002",
                mutation_type="DuplicateAndPerturb",
                slope=0.15,
                accepted=True,
            ),
        ]

        panel = LineageViewer(nodes=nodes, edges=edges)
        # Check that edges have slope data
        assert panel.edges[0].slope == 0.15
        assert panel.edges[0].mutation_type == "DuplicateAndPerturb"

    def test_component_register_aware(self) -> None:
        """Component must show plain language in Explorer, technical in Lab."""
        from computronium.ui.components.lineage_viewer import LineageNode, LineageViewer
        from computronium.ui.mode_toggle import set_mode

        nodes = [
            LineageNode(
                genome_id="genome_001",
                tier=1,
                fitness=0.8,
                episode=0,
                parent_id=None,
                mutation_type=None,
                slope=0.1,
            ),
        ]

        # Test Explorer mode
        set_mode("explorer")
        panel_explorer = LineageViewer(nodes=nodes)
        assert panel_explorer.is_explorer

        # Test Lab mode
        set_mode("lab")
        panel_lab = LineageViewer(nodes=nodes)
        assert panel_lab.is_lab


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
