"""Full sections parsing."""

from .blog import read_blog
from .home import read_homepage

__all__ = [
    'read_blog',
    'read_homepage',
]
