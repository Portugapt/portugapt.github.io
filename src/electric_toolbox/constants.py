"""Constants for the electric toolbox."""

from enum import Enum, auto


class ExistingTemplates(Enum):
    """Enum of full-page templates.

    With hx-boost there is one document per page; htmx fetches it and swaps
    ``#body-content`` on navigation, so no separate fragment templates exist.
    """

    INDEX = auto()
    BLOG_INDEX = auto()
    BLOG_ARTICLE = auto()
