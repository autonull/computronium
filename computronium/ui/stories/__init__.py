"""Story gallery — one module per panel, rendered standalone (GAME.todo7 §5.2)."""

from computronium.ui.stories.gallery import (
    STORIES,
    Story,
    build_story,
    main,
    register_story,
    serve,
)

__all__ = [
    "STORIES",
    "Story",
    "build_story",
    "main",
    "register_story",
    "serve",
]
