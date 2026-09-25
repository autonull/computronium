"""Virtualization Utilities — efficient rendering of large lists.

Provides:
- VirtualScroller: windowed rendering for vertical lists
- VirtualGrid: windowed rendering for grid layouts
- Auto-height measurement
- Overscan for smooth scrolling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from nicegui import ui

T = TypeVar("T")


@dataclass
class VirtualItem(Generic[T]):
    """An item in the virtualized list."""
    index: int
    data: T
    top: float = 0
    height: float = 0
    visible: bool = False


@dataclass
class VirtualRange:
    """Visible range of items."""
    start: int
    end: int
    overscan_start: int
    overscan_end: int


class VirtualScroller(Generic[T]):
    """Virtual scroller for large vertical lists.
    
    Only renders items in the visible viewport + overscan.
    Measures item heights dynamically for variable-height items.
    """
    
    def __init__(
        self,
        items: list[T],
        render_item: Callable[[T, int], Any],
        *,
        item_height: float | Callable[[T], float] = 50,
        overscan: int = 5,
        container_height: float = 400,
        estimate_height: bool = True,
    ):
        self.items = items
        self.render_item = render_item
        self.overscan = overscan
        self.container_height = container_height
        self.estimate_height = estimate_height
        
        # Height function
        if callable(item_height):
            self._get_height = item_height
        else:
            self._get_height = lambda _: item_height
        
        # State
        self._scroll_top = 0
        self._item_heights: dict[int, float] = {}
        self._measured_heights: dict[int, float] = {}
        self._range = VirtualRange(0, 0, 0, 0)
        self._container: Any = None
        self._content: Any = None
        self._scroll_handler: Any = None
        
        # Callbacks
        self.on_range_change: Callable[[VirtualRange], None] | None = None
        self.on_scroll: Callable[[float], None] | None = None

    @property
    def total_height(self) -> float:
        """Total scrollable height."""
        return sum(self._get_item_height(i) for i in range(len(self.items)))

    @property
    def visible_range(self) -> VirtualRange:
        """Get current visible range."""
        return self._range

    def _get_item_height(self, index: int) -> float:
        """Get height for item at index."""
        # Use measured height if available
        if index in self._measured_heights:
            return self._measured_heights[index]
        # Use estimated height
        return self._get_height(self.items[index])

    def _calculate_range(self, scroll_top: float) -> VirtualRange:
        """Calculate visible range for scroll position."""
        if not self.items:
            return VirtualRange(0, 0, 0, 0)
        
        # Find start index
        accumulated = 0
        start = 0
        for i in range(len(self.items)):
            height = self._get_item_height(i)
            if accumulated + height > scroll_top:
                start = i
                break
            accumulated += height
        
        # Find end index
        accumulated = 0
        for i in range(start, len(self.items)):
            height = self._get_item_height(i)
            if accumulated > self.container_height:
                break
            accumulated += height
        end = min(i + 1, len(self.items))
        
        # Apply overscan
        overscan_start = max(0, start - self.overscan)
        overscan_end = min(len(self.items), end + self.overscan)
        
        return VirtualRange(start, end, overscan_start, overscan_end)

    def update_scroll(self, scroll_top: float) -> None:
        """Update scroll position and recalculate range."""
        self._scroll_top = max(0, min(scroll_top, self.total_height - self.container_height))
        new_range = self._calculate_range(self._scroll_top)
        
        if (new_range.start != self._range.start or 
            new_range.end != self._range.end):
            self._range = new_range
            if self.on_range_change:
                self.on_range_change(new_range)
        
        if self.on_scroll:
            self.on_scroll(self._scroll_top)

    def measure_item(self, index: int, height: float) -> None:
        """Record measured height for item."""
        if self.estimate_height:
            self._measured_heights[index] = height

    def get_visible_items(self) -> list[VirtualItem[T]]:
        """Get virtual items for current range."""
        result = []
        top = 0
        
        # Calculate top position for overscan_start
        for i in range(self._range.overscan_start):
            top += self._get_item_height(i)
        
        for i in range(self._range.overscan_start, self._range.overscan_end):
            height = self._get_item_height(i)
            result.append(VirtualItem(
                index=i,
                data=self.items[i],
                top=top,
                height=height,
                visible=(self._range.start <= i < self._range.end)
            ))
            top += height
        
        return result

    def scroll_to(self, index: int, align: str = "start") -> float:
        """Calculate scroll position to bring item into view."""
        if index < 0 or index >= len(self.items):
            return self._scroll_top
        
        # Calculate item top
        item_top = sum(self._get_item_height(i) for i in range(index))
        item_height = self._get_item_height(index)
        
        if align == "start":
            return item_top
        elif align == "end":
            return item_top + item_height - self.container_height
        elif align == "center":
            return item_top - (self.container_height - item_height) / 2
        else:  # "nearest"
            if item_top < self._scroll_top:
                return item_top
            elif item_top + item_height > self._scroll_top + self.container_height:
                return item_top + item_height - self.container_height
            return self._scroll_top

    def refresh(self) -> None:
        """Refresh after items change."""
        self._measured_heights.clear()
        self.update_scroll(self._scroll_top)

    def set_items(self, items: list[T]) -> None:
        """Replace items list."""
        self.items = items
        self.refresh()


class VirtualGrid(Generic[T]):
    """Virtual scroller for grid layouts."""
    
    def __init__(
        self,
        items: list[T],
        render_item: Callable[[T, int], Any],
        *,
        columns: int = 4,
        item_height: float | Callable[[T], float] = 200,
        item_width: float | Callable[[T], float] = 200,
        gap: float = 16,
        container_width: float = 800,
        container_height: float = 400,
        overscan: int = 2,
    ):
        self.items = items
        self.render_item = render_item
        self.columns = columns
        self.gap = gap
        self.container_width = container_width
        self.container_height = container_height
        self.overscan = overscan
        
        if callable(item_height):
            self._get_height = item_height
        else:
            self._get_height = lambda _: item_height
            
        if callable(item_width):
            self._get_width = item_width
        else:
            self._get_width = lambda _: item_width
        
        self._scroll_top = 0
        self._measured_heights: dict[int, float] = {}
        self._range = VirtualRange(0, 0, 0, 0)
        
        self.on_range_change: Callable[[VirtualRange], None] | None = None
        self.on_scroll: Callable[[float], None] | None = None

    @property
    def total_rows(self) -> int:
        return (len(self.items) + self.columns - 1) // self.columns

    @property
    def total_height(self) -> float:
        if not self.items:
            return 0
        row_heights = []
        for row in range(self.total_rows):
            max_h = 0
            for col in range(self.columns):
                idx = row * self.columns + col
                if idx < len(self.items):
                    h = self._get_item_height(idx)
                    max_h = max(max_h, h)
            row_heights.append(max_h)
        return sum(row_heights) + self.gap * (self.total_rows - 1)

    def _get_item_height(self, index: int) -> float:
        if index in self._measured_heights:
            return self._measured_heights[index]
        return self._get_height(self.items[index])

    def _get_item_width(self, index: int) -> float:
        return self._get_width(self.items[index])

    def _calculate_range(self, scroll_top: float) -> VirtualRange:
        if not self.items:
            return VirtualRange(0, 0, 0, 0)
        
        # Find start row
        accumulated = 0
        start_row = 0
        for row in range(self.total_rows):
            max_h = 0
            for col in range(self.columns):
                idx = row * self.columns + col
                if idx < len(self.items):
                    max_h = max(max_h, self._get_item_height(idx))
            row_h = max_h + (self.gap if row > 0 else 0)
            if accumulated + row_h > scroll_top:
                start_row = row
                break
            accumulated += row_h
        
        # Find end row
        accumulated = 0
        for row in range(start_row, self.total_rows):
            max_h = 0
            for col in range(self.columns):
                idx = row * self.columns + col
                if idx < len(self.items):
                    max_h = max(max_h, self._get_item_height(idx))
            row_h = max_h + (self.gap if row > 0 else 0)
            if accumulated > self.container_height:
                break
            accumulated += row_h
        end_row = min(row + 1, self.total_rows)
        
        start = start_row * self.columns
        end = min(end_row * self.columns, len(self.items))
        overscan_start = max(0, start - self.overscan * self.columns)
        overscan_end = min(len(self.items), end + self.overscan * self.columns)
        
        return VirtualRange(start, end, overscan_start, overscan_end)

    def update_scroll(self, scroll_top: float) -> None:
        self._scroll_top = max(0, min(scroll_top, max(0, self.total_height - self.container_height)))
        new_range = self._calculate_range(self._scroll_top)
        
        if (new_range.start != self._range.start or 
            new_range.end != self._range.end):
            self._range = new_range
            if self.on_range_change:
                self.on_range_change(new_range)
        
        if self.on_scroll:
            self.on_scroll(self._scroll_top)

    def get_visible_items(self) -> list[VirtualItem[T]]:
        result = []
        for i in range(self._range.overscan_start, self._range.overscan_end):
            row = i // self.columns
            col = i % self.columns
            
            # Calculate position
            top = 0
            for r in range(row):
                max_h = 0
                for c in range(self.columns):
                    idx = r * self.columns + c
                    if idx < len(self.items):
                        max_h = max(max_h, self._get_item_height(idx))
                top += max_h + (self.gap if r > 0 else 0)
            
            left = 0
            for c in range(col):
                idx = row * self.columns + c
                if idx < len(self.items):
                    left += self._get_item_width(idx) + self.gap
            
            height = self._get_item_height(i)
            width = self._get_item_width(i)
            
            result.append(VirtualItem(
                index=i,
                data=self.items[i],
                top=top,
                height=height,
                visible=(self._range.start <= i < self._range.end)
            ))
        return result

    def measure_item(self, index: int, height: float) -> None:
        self._measured_heights[index] = height

    def refresh(self) -> None:
        self._measured_heights.clear()
        self.update_scroll(self._scroll_top)

    def set_items(self, items: list[T]) -> None:
        self.items = items
        self.refresh()


# ──────────────────────────────────────────────────────────────────────────────
# NiceGUI Integration Helpers
# ──────────────────────────────────────────────────────────────────────────────

def create_virtual_list(
    items: list[T],
    render_item: Callable[[T, int], Any],
    *,
    height: float = 400,
    item_height: float | Callable[[T], float] = 50,
    overscan: int = 5,
) -> tuple[VirtualScroller[T], "ui.column"]:
    """Create a virtualized list with NiceGUI container."""
    from nicegui import ui
    
    scroller = VirtualScroller(
        items=items,
        render_item=render_item,
        item_height=item_height,
        overscan=overscan,
        container_height=height,
    )
    
    container = ui.column().classes("w-full overflow-auto").style(f"height: {height}px")
    content = ui.column().classes("w-full").style(f"min-height: {scroller.total_height}px")
    
    def on_scroll(e: Any) -> None:
        scroll_top = e.args.get("scrollTop", 0) if hasattr(e, "args") else 0
        scroller.update_scroll(scroll_top)
        _render_visible()
    
    def _render_visible() -> None:
        content.clear()
        with content:
            for vitem in scroller.get_visible_items():
                with ui.column().style(f"position: absolute; top: {vitem.top}px; height: {vitem.height}px; width: 100%;"):
                    element = render_item(vitem.data, vitem.index)
                    if hasattr(element, 'on'):
                        def on_mounted(e, idx=vitem.index):
                            if hasattr(e, 'sender') and hasattr(e.sender, 'offsetHeight'):
                                scroller.measure_item(idx, e.sender.offsetHeight)
                        element.on('mounted', on_mounted)
    
    container.on("scroll", on_scroll)
    _render_visible()
    
    return scroller, container


def create_virtual_grid(
    items: list[T],
    render_item: Callable[[T, int], Any],
    *,
    columns: int = 4,
    height: float = 400,
    item_height: float | Callable[[T], float] = 200,
    item_width: float | Callable[[T], float] = 200,
    gap: float = 16,
    overscan: int = 2,
) -> tuple[VirtualGrid[T], "ui.column"]:
    """Create a virtualized grid with NiceGUI container."""
    from nicegui import ui
    
    grid = VirtualGrid(
        items=items,
        render_item=render_item,
        columns=columns,
        item_height=item_height,
        item_width=item_width,
        gap=gap,
        container_height=height,
        overscan=overscan,
    )
    
    container = ui.column().classes("w-full overflow-auto").style(f"height: {height}px")
    content = ui.column().classes("w-full").style(f"min-height: {grid.total_height}px")
    
    def on_scroll(e: Any) -> None:
        scroll_top = e.args.get("scrollTop", 0) if hasattr(e, "args") else 0
        grid.update_scroll(scroll_top)
        _render_visible()
    
    def _render_visible() -> None:
        content.clear()
        with content:
            for vitem in grid.get_visible_items():
                row = vitem.index // columns
                col = vitem.index % columns
                
                with ui.column().style(
                    f"position: absolute; top: {vitem.top}px; left: {col * (200 + gap)}px; "
                    f"height: {vitem.height}px; width: {item_width(vitem.data) if callable(item_width) else item_width}px;"
                ):
                    element = render_item(vitem.data, vitem.index)
                    if hasattr(element, 'on'):
                        def on_mounted(e, idx=vitem.index):
                            if hasattr(e, 'sender') and hasattr(e.sender, 'offsetHeight'):
                                grid.measure_item(idx, e.sender.offsetHeight)
                        element.on('mounted', on_mounted)
    
    container.on("scroll", on_scroll)
    _render_visible()
    
    return grid, container


# ──────────────────────────────────────────────────────────────────────────────
# Pagination Alternative (for simpler cases)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PaginatedList(Generic[T]):
    """Simple pagination for lists that don't need virtualization."""
    
    items: list[T]
    page_size: int = 50
    current_page: int = 0
    
    @property
    def total_pages(self) -> int:
        return max(1, (len(self.items) + self.page_size - 1) // self.page_size)
    
    @property
    def page_items(self) -> list[T]:
        start = self.current_page * self.page_size
        end = min(start + self.page_size, len(self.items))
        return self.items[start:end]
    
    @property
    def page_range(self) -> tuple[int, int]:
        start = self.current_page * self.page_size
        end = min(start + self.page_size, len(self.items))
        return (start, end)
    
    def next_page(self) -> bool:
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            return True
        return False
    
    def prev_page(self) -> bool:
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False
    
    def go_to_page(self, page: int) -> bool:
        if 0 <= page < self.total_pages:
            self.current_page = page
            return True
        return False
    
    def render(self, render_item: Callable[[T, int], Any], render_pagination: Callable[[], Any] | None = None) -> Any:
        from nicegui import ui
        
        with ui.column().classes("w-full gap-4") as container:
            # Items
            with ui.column().classes("w-full gap-2") as items_container:
                for i, item in enumerate(self.page_items):
                    render_item(item, self.current_page * self.page_size + i)
            
            # Pagination
            if render_pagination:
                render_pagination()
            elif self.total_pages > 1:
                with ui.row().classes("w-full justify-center gap-2"):
                    ui.button("←", on_click=lambda: (self.prev_page(), container.update())).props("flat")
                    ui.label(f"Page {self.current_page + 1} of {self.total_pages}")
                    ui.button("→", on_click=lambda: (self.next_page(), container.update())).props("flat")
        
        return container