"""Tests for Pareto front analysis functions (E2, §7.1)."""

from __future__ import annotations

import numpy as np
import pytest

from computronium.experiment.evidence.statistics import (
    hypervolume,
    knee_detection,
    pareto_front,
)


class TestParetoFront:
    """Tests for pareto_front function."""

    def test_simple_2d_front(self) -> None:
        """Basic 2D minimization front."""
        points = np.array([
            [1.0, 5.0],   # dominated by [1, 3]
            [2.0, 4.0],   # dominated by [1, 3]
            [1.0, 3.0],   # on front
            [3.0, 1.0],   # on front
            [4.0, 2.0],   # dominated by [3, 1]
        ])
        mask = pareto_front(points)
        assert mask.tolist() == [False, False, True, True, False]

    def test_all_dominated_by_one(self) -> None:
        """One point dominates all others."""
        points = np.array([
            [1.0, 1.0],   # dominates all
            [2.0, 2.0],
            [3.0, 3.0],
        ])
        mask = pareto_front(points)
        assert mask.tolist() == [True, False, False]

    def test_all_on_front_tie(self) -> None:
        """All points identical — all on front."""
        points = np.array([
            [1.0, 2.0],
            [1.0, 2.0],
            [1.0, 2.0],
        ])
        mask = pareto_front(points)
        assert mask.tolist() == [True, True, True]

    def test_maximize_direction(self) -> None:
        """Test with maximize=True for some objectives."""
        points = np.array([
            [1.0, 1.0],   # low on both
            [5.0, 5.0],   # high on both - should dominate if maximize
            [3.0, 3.0],
        ])
        # Maximize both
        mask = pareto_front(points, maximize=[True, True])
        assert mask.tolist() == [False, True, False]

    def test_mixed_directions(self) -> None:
        """Minimize first, maximize second."""
        points = np.array([
            [1.0, 1.0],   # good on first, bad on second
            [2.0, 5.0],   # bad on first, good on second
            [3.0, 3.0],   # middle
        ])
        mask = pareto_front(points, maximize=[False, True])
        # [1, 1] and [2, 5] should both be on front
        assert mask.tolist() == [True, True, False]

    def test_3d_front(self) -> None:
        """3 objectives."""
        points = np.array([
            [1.0, 1.0, 1.0],  # dominates all
            [2.0, 2.0, 2.0],
            [1.5, 1.5, 1.5],
        ])
        mask = pareto_front(points)
        assert mask.tolist() == [True, False, False]

    def test_empty_array(self) -> None:
        """Empty array returns empty mask."""
        points = np.array([]).reshape(0, 2)
        mask = pareto_front(points)
        assert mask.shape == (0,)
        assert mask.dtype == bool

    def test_single_point(self) -> None:
        """Single point is always on front."""
        points = np.array([[1.0, 2.0]])
        mask = pareto_front(points)
        assert mask.tolist() == [True]

    def test_invalid_shape_raises(self) -> None:
        """1D array raises ValueError."""
        points = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError, match="2D array"):
            pareto_front(points)

    def test_wrong_maximize_length_raises(self) -> None:
        """Mismatched maximize length raises ValueError."""
        points = np.array([[1.0, 2.0]])
        with pytest.raises(ValueError, match="1 directions but 2 objectives"):
            pareto_front(points, maximize=[True])


class TestHypervolume:
    """Tests for hypervolume function."""

    def test_simple_2d_area(self) -> None:
        """2D hypervolume = area."""
        # Front: (1, 3) and (3, 1), reference (5, 5)
        # Area = (5-1)*(5-3) + (5-3)*(5-1) - overlap = 8 + 8 - 4 = 12
        # Actually the hypervolume is the union of rectangles
        front = np.array([[1.0, 3.0], [3.0, 1.0]])
        ref = np.array([5.0, 5.0])
        hv = hypervolume(front, reference=ref)
        # Each point contributes: (5-1)*(5-3)=8 and (5-3)*(5-1)=8
        # But they overlap in [3,5]x[3,5] which is 4, so total = 12
        assert abs(hv - 12.0) < 1e-6

    def test_single_point(self) -> None:
        """Single point hypervolume."""
        front = np.array([[2.0, 3.0]])
        ref = np.array([5.0, 5.0])
        hv = hypervolume(front, reference=ref)
        assert abs(hv - (5.0 - 2.0) * (5.0 - 3.0)) < 1e-6  # = 6

    def test_empty_front(self) -> None:
        """Empty front returns 0."""
        front = np.array([]).reshape(0, 2)
        hv = hypervolume(front, reference=np.array([5.0, 5.0]))
        assert hv == 0.0

    def test_auto_reference(self) -> None:
        """Auto-computed reference point."""
        front = np.array([[1.0, 2.0], [2.0, 1.0]])
        hv = hypervolume(front)
        # Should use max + 1e-6 as reference
        assert hv > 0.0

    def test_maximize_direction(self) -> None:
        """Hypervolume with maximize direction."""
        front = np.array([[5.0, 5.0], [3.0, 3.0]])  # Higher is better
        ref = np.array([0.0, 0.0])  # Reference is worse (lower)
        hv = hypervolume(front, reference=ref, maximize=[True, True])
        assert hv > 0.0

    def test_3d_volume(self) -> None:
        """3D hypervolume = volume."""
        # Point (1,1,1) dominates (2,2,2), so front is just (1,1,1)
        # Volume = (5-1)^3 = 64
        front = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])
        ref = np.array([5.0, 5.0, 5.0])
        hv = hypervolume(front, reference=ref)
        assert abs(hv - 64.0) < 1e-6

    def test_reference_must_dominate(self) -> None:
        """Reference that doesn't dominate raises error."""
        front = np.array([[5.0, 5.0]])
        ref = np.array([3.0, 3.0])  # Better than front, doesn't dominate
        with pytest.raises(ValueError, match="must dominate"):
            hypervolume(front, reference=ref)

    def test_wrong_reference_shape(self) -> None:
        """Wrong reference shape raises error."""
        front = np.array([[1.0, 2.0]])
        ref = np.array([5.0])  # 1D but front is 2D
        with pytest.raises(ValueError, match="shape"):
            hypervolume(front, reference=ref)


class TestKneeDetection:
    """Tests for knee_detection function."""

    def test_simple_2d_knee(self) -> None:
        """Clear knee in 2D - asymmetric front."""
        # Asymmetric front: knee should be at the bend
        front = np.array([[1.0, 10.0], [3.0, 4.0], [10.0, 1.0]])
        idx = knee_detection(front)
        # The middle point (3, 4) is the knee (furthest from line connecting extremes)
        assert idx == 1

    def test_symmetric_l_shape_knee_at_middle(self) -> None:
        """Symmetric L-shape has knee at middle (endpoints excluded)."""
        front = np.array([[1.0, 10.0], [5.0, 5.0], [10.0, 1.0]])
        idx = knee_detection(front)
        # Middle point is the only interior point, so it's the knee
        assert idx == 1

    def test_knee_at_middle_for_linear(self) -> None:
        """For linear front, middle point is returned (endpoints excluded)."""
        front = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]])
        idx = knee_detection(front)
        # All interior distances are ~0, so middle is picked by fallback
        assert idx == 1

    def test_two_points_returns_minus_one(self) -> None:
        """Two points has no well-defined knee."""
        front = np.array([[1.0, 10.0], [10.0, 1.0]])
        idx = knee_detection(front)
        assert idx == -1

    def test_single_point_raises(self) -> None:
        """Single point raises ValueError."""
        front = np.array([[1.0, 2.0]])
        with pytest.raises(ValueError, match="at least 2 points"):
            knee_detection(front)

    def test_maximize_direction(self) -> None:
        """Knee detection with maximize direction."""
        front = np.array([[1.0, 10.0], [5.0, 5.0], [10.0, 1.0]])
        # Maximize both - front is same but interpretation flips
        idx = knee_detection(front, maximize=[True, True])
        assert idx in {0, 1, 2}

    def test_no_normalize(self) -> None:
        """Knee detection without normalization."""
        front = np.array([[1.0, 100.0], [50.0, 50.0], [100.0, 1.0]])
        idx = knee_detection(front, normalize=False)
        # Without normalization, scale differences affect knee
        assert idx in {0, 1, 2}

    def test_all_identical_points(self) -> None:
        """All identical points returns a valid index."""
        front = np.array([[5.0, 5.0], [5.0, 5.0], [5.0, 5.0]])
        idx = knee_detection(front)
        assert idx in {0, 1}  # All points identical, any is valid


class TestParetoIntegration:
    """Integration tests combining pareto_front, hypervolume, knee_detection."""

    def test_full_pipeline_2d(self) -> None:
        """Full pipeline: pareto_front -> hypervolume -> knee_detection."""
        points = np.array([
            [1.0, 8.0],
            [2.0, 6.0],
            [3.0, 4.0],
            [4.0, 3.0],
            [5.0, 2.5],
            [6.0, 2.0],
            [7.0, 1.5],
            [8.0, 1.0],
        ])
        # Get Pareto front
        mask = pareto_front(points)
        front = points[mask]
        # Compute hypervolume
        hv = hypervolume(front, reference=np.array([10.0, 10.0]))
        assert hv > 0.0
        # Find knee
        knee_idx = knee_detection(front)
        assert 0 <= knee_idx < len(front)

    def test_3d_pipeline(self) -> None:
        """Full pipeline in 3D."""
        points = np.array([
            [1.0, 1.0, 1.0],
            [2.0, 2.0, 2.0],
            [1.0, 2.0, 3.0],
            [3.0, 1.0, 2.0],
            [2.0, 3.0, 1.0],
        ])
        mask = pareto_front(points)
        front = points[mask]
        assert len(front) >= 1
        hv = hypervolume(front, reference=np.array([5.0, 5.0, 5.0]))
        assert hv > 0.0
        if len(front) >= 3:
            knee_idx = knee_detection(front)
            assert 0 <= knee_idx < len(front)
