"""Constants for the electric toolbox."""

from enum import Enum, auto


class ExistingTemplates(Enum):
    """Enum of templates for paging."""

    INDEX = auto()
    INDEX_HX = auto()
    BLOG_INDEX = auto()
    BLOG_INDEX_HX = auto()
    BLOG_ARTICLE = auto()
    BLOG_ARTICLE_HX = auto()
