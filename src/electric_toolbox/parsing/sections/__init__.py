"""Full sections parsing."""

from .blog import ViewModelBlog, ViewModelBlogPost, read_blog
from .home import ViewModelHomePage, read_homepage

__all__ = [
    'ViewModelBlog',
    'ViewModelBlogPost',
    'ViewModelHomePage',
    'read_blog',
    'read_homepage',
]
