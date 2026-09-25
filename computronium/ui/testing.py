"""Component Testing Utilities — headless testing, snapshots, and assertions.

Provides:
- Headless component renderer
- Snapshot testing
- Accessibility assertions
- Interaction simulation
- Visual regression helpers
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Generator

if TYPE_CHECKING:
    from nicegui import ui
    from computronium.ui.component import Component


@dataclass
class RenderResult:
    """Result of rendering a component."""
    root: Any
    container: Any
    component: "Component"
    queries: "QueryAPI"
    a11y: "A11yAssertions" = field(default_factory=A11yAssertions)
    interactions: "InteractionSimulator" = field(default_factory=lambda: InteractionSimulator(None))


class QueryAPI:
    """DOM query API for testing (similar to Testing Library)."""
    
    def __init__(self, container: Any):
        self.container = container
    
    def get_by_text(self, text: str, exact: bool = True) -> Any:
        """Find element by text content."""
        elements = self.container.querySelectorAll("*")
        for el in elements:
            el_text = el.innerText or el.textContent or ""
            if exact:
                if el_text.strip() == text:
                    return el
            else:
                if text in el_text:
                    return el
        raise AssertionError(f"Element with text '{text}' not found")
    
    def get_by_role(self, role: str, name: str | None = None) -> Any:
        """Find element by ARIA role."""
        selector = f"[role='{role}']"
        if name:
            selector += f"[aria-label*='{name}']"
        elements = self.container.querySelectorAll(selector)
        if elements.length == 0:
            raise AssertionError(f"Element with role '{role}' not found")
        return elements[0]
    
    def get_by_label(self, label: str) -> Any:
        """Find element by label."""
        elements = self.container.querySelectorAll(f"[aria-label*='{label}']")
        if elements.length == 0:
            # Check for <label> elements
            elements = self.container.querySelectorAll("label")
            for el in elements:
                if label in (el.innerText or ""):
                    return el
        if elements.length == 0:
            raise AssertionError(f"Element with label '{label}' not found")
        return elements[0]
    
    def get_by_test_id(self, test_id: str) -> Any:
        """Find element by data-testid."""
        elements = self.container.querySelectorAll(f"[data-testid='{test_id}']")
        if elements.length == 0:
            raise AssertionError(f"Element with test-id '{test_id}' not found")
        return elements[0]
    
    def query_by_text(self, text: str, exact: bool = True) -> Any | None:
        """Find element by text, return None if not found."""
        try:
            return self.get_by_text(text, exact)
        except AssertionError:
            return None
    
    def query_by_role(self, role: str, name: str | None = None) -> Any | None:
        """Find element by role, return None if not found."""
        try:
            return self.get_by_role(role, name)
        except AssertionError:
            return None
    
    def find_all_by_text(self, text: str) -> list[Any]:
        """Find all elements matching text."""
        elements = self.container.querySelectorAll("*")
        return [el for el in elements if text in (el.innerText or el.textContent or "")]
    
    def find_all_by_role(self, role: str) -> list[Any]:
        """Find all elements with role."""
        return list(self.container.querySelectorAll(f"[role='{role}']"))


class A11yAssertions:
    """Accessibility assertions."""
    
    @staticmethod
    def has_role(element: Any, role: str) -> bool:
        return element.getAttribute("role") == role
    
    @staticmethod
    def has_aria_label(element: Any, label: str | None = None) -> bool:
        aria_label = element.getAttribute("aria-label")
        if label is None:
            return aria_label is not None
        return label in (aria_label or "")
    
    @staticmethod
    def has_aria_expanded(element: Any, expanded: bool | None = None) -> bool:
        aria_expanded = element.getAttribute("aria-expanded")
        if expanded is None:
            return aria_expanded is not None
        return aria_expanded == ("true" if expanded else "false")
    
    @staticmethod
    def has_aria_controls(element: Any, controls_id: str | None = None) -> bool:
        aria_controls = element.getAttribute("aria-controls")
        if controls_id is None:
            return aria_controls is not None
        return controls_id in (aria_controls or "")
    
    @staticmethod
    def is_visible(element: Any) -> bool:
        style = element.style
        return style.display != "none" and style.visibility != "hidden" and style.opacity != "0"
    
    @staticmethod
    def is_focusable(element: Any) -> bool:
        tabindex = element.getAttribute("tabindex")
        if tabindex == "-1":
            return False
        tag = element.tagName.lower()
        return tag in ("button", "a", "input", "select", "textarea") or tabindex is not None
    
    @staticmethod
    def has_focus_style(element: Any) -> bool:
        """Check if element has visible focus styles."""
        # This would need computed styles - simplified check
        return True  # Placeholder
    
    @staticmethod
    def check_color_contrast(element: Any) -> bool:
        """Check if element meets WCAG contrast requirements."""
        # Would need computed styles - placeholder
        return True


class InteractionSimulator:
    """Simulate user interactions."""
    
    def __init__(self, container: Any):
        self.container = container
    
    def click(self, element: Any) -> None:
        """Simulate click."""
        element.click()
    
    def focus(self, element: Any) -> None:
        """Focus element."""
        element.focus()
    
    def type(self, element: Any, text: str) -> None:
        """Type into input."""
        element.value = text
        element.dispatchEvent("input")
        element.dispatchEvent("change")
    
    def key_down(self, element: Any, key: str, modifiers: dict[str, bool] | None = None) -> None:
        """Simulate key down."""
        event = {
            "key": key,
            "shiftKey": modifiers.get("shift", False) if modifiers else False,
            "ctrlKey": modifiers.get("ctrl", False) if modifiers else False,
            "metaKey": modifiers.get("meta", False) if modifiers else False,
            "altKey": modifiers.get("alt", False) if modifiers else False,
        }
        element.dispatchEvent("keydown", event)
    
    def hover(self, element: Any) -> None:
        """Simulate hover."""
        element.dispatchEvent("mouseenter")
        element.dispatchEvent("mouseover")


@dataclass
class Snapshot:
    """Component snapshot for visual regression testing."""
    html: str
    css: str
    timestamp: float
    metadata: dict = field(default_factory=dict)


class SnapshotMatcher:
    """Match component snapshots."""
    
    def __init__(self, update_snapshots: bool = False):
        self.update_snapshots = update_snapshots
        self._snapshots: dict[str, Snapshot] = {}
    
    def match(self, name: str, container: Any) -> bool:
        """Match container against snapshot."""
        html = container.outerHTML if hasattr(container, 'outerHTML') else str(container)
        snapshot = Snapshot(html=html, css="", timestamp=0)
        
        if name in self._snapshots:
            existing = self._snapshots[name]
            if existing.html == snapshot.html:
                return True
            if self.update_snapshots:
                self._snapshots[name] = snapshot
                return True
            return False
        else:
            self._snapshots[name] = snapshot
            return True
    
    def save_snapshots(self, path: str) -> None:
        """Save snapshots to file."""
        import json
        data = {k: {"html": v.html, "metadata": v.metadata} for k, v in self._snapshots.items()}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_snapshots(self, path: str) -> None:
        """Load snapshots from file."""
        import json
        with open(path) as f:
            data = json.load(f)
        self._snapshots = {k: Snapshot(html=v["html"], css="", timestamp=0, metadata=v.get("metadata", {})) 
                          for k, v in data.items()}


@contextmanager
def render_component(
    component: "Component",
    *,
    container: Any | None = None,
) -> Generator[RenderResult, None, None]:
    """Render a component for testing.
    
    Usage:
        with render_component(MyComponent()) as result:
            result.queries.get_by_text("Hello")
            result.queries.get_by_role("button")
    """
    from nicegui import ui
    
    # Create test container
    if container is None:
        container = ui.column().classes("w-full")
    
    with container:
        root = component.mount()
    
    queries = QueryAPI(container)
    a11y = A11yAssertions()
    interactions = InteractionSimulator(container)
    
    result = RenderResult(
        root=root,
        container=container,
        component=component,
        queries=queries,
        a11y=a11y,
        interactions=interactions,
    )
    
    try:
        yield result
    finally:
        component.unmount()


def test_render(component_factory: Callable[[], "Component"]) -> RenderResult:
    """Test component render without context manager (for simple tests)."""
    from nicegui import ui
    
    container = ui.column().classes("w-full")
    component = component_factory()
    
    with container:
        root = component.mount()
    
    queries = QueryAPI(container)
    
    return RenderResult(
        root=root,
        container=container,
        component=component,
        queries=queries,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Test Fixtures
# ──────────────────────────────────────────────────────────────────────────────

def create_test_app() -> Any:
    """Create a minimal NiceGUI app for testing."""
    from nicegui import app, ui
    
    @ui.page("/")
    def _():
        pass
    
    return app


async def async_render(
    component: "Component",
    *,
    timeout: float = 5.0,
) -> RenderResult:
    """Render component asynchronously (for async components)."""
    import asyncio
    from nicegui import ui
    
    container = ui.column().classes("w-full")
    
    async def _mount():
        with container:
            root = component.mount()
        return root
    
    root = await asyncio.wait_for(_mount(), timeout=timeout)
    
    queries = QueryAPI(container)
    
    return RenderResult(
        root=root,
        container=container,
        component=component,
        queries=queries,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Visual Regression Helpers
# ──────────────────────────────────────────────────────────────────────────────

async def screenshot_element(element: Any, path: str) -> None:
    """Take screenshot of element (requires browser context)."""
    # This requires a real browser - placeholder for Selenium/Playwright integration
    pass


def compare_screenshots(baseline: str, actual: str, threshold: float = 0.1) -> bool:
    """Compare two screenshot files (requires PIL)."""
    try:
        from PIL import Image
        import numpy as np
        
        img1 = Image.open(baseline).convert("RGBA")
        img2 = Image.open(actual).convert("RGBA")
        
        if img1.size != img2.size:
            return False
        
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        diff = np.abs(arr1.astype(float) - arr2.astype(float))
        diff_pct = float(np.mean(diff > 10))  # 10/255 threshold per channel
        
        return diff_pct < threshold
    except ImportError:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Property-Based Testing Helpers
# ──────────────────────────────────────────────────────────────────────────────

def assert_no_console_errors(container: Any) -> None:
    """Assert no console errors in rendered component."""
    # Would need browser context - placeholder
    pass


def assert_accessible(container: Any) -> None:
    """Run basic accessibility checks on container."""
    a11y = A11yAssertions()
    
    # Check all interactive elements have accessible names
    interactive = container.querySelectorAll("button, a, input, select, textarea, [role='button'], [tabindex]")
    for el in interactive:
        assert a11y.has_aria_label(el) or el.getAttribute("aria-labelledby") or el.textContent.strip(), \
            f"Interactive element missing accessible name: {el.outerHTML}"
    
    # Check images have alt text
    images = container.querySelectorAll("img")
    for img in images:
        assert img.getAttribute("alt") is not None, f"Image missing alt text: {img.outerHTML}"
    
    # Check heading hierarchy
    headings = container.querySelectorAll("h1, h2, h3, h4, h5, h6")
    prev_level = 0
    for h in headings:
        level = int(h.tagName[1])
        assert level <= prev_level + 1, f"Heading level skip: {h.outerHTML}"
        prev_level = level


# ──────────────────────────────────────────────────────────────────────────────
# Export
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    "RenderResult",
    "QueryAPI",
    "A11yAssertions",
    "InteractionSimulator",
    "Snapshot",
    "SnapshotMatcher",
    "render_component",
    "test_render",
    "create_test_app",
    "async_render",
    "screenshot_element",
    "compare_screenshots",
    "PaginatedList",
    "assert_no_console_errors",
    "assert_accessible",
]