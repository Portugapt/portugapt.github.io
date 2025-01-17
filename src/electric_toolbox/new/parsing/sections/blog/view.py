"""Views for the blog."""

from electric_toolbox.new.parsing.components.breadcrumbs import create_breadcrumbs_view_model
from electric_toolbox.new.parsing.components.navigation import create_navigation_view_model
from electric_toolbox.new.parsing.components.opengraph import (
    create_opengraph_article_view_model,
    create_opengraph_view_model,
)

from .models import Blog, BlogPost, ViewModelBlog, ViewModelBlogPost


def create_blogpost_view_model(
    post: BlogPost,
) -> ViewModelBlogPost:
    """Prepares the view model for a blog post.

    Args:
        post: The blog post.
        base_url: The base URL of the site.

    Returns:
        The view model for the blog post.
    """
    return ViewModelBlogPost(
        title=post.title,
        date=post.date,
        contents=post.contents,
        base_url=str(post.base_url),
        resource_path=str(post.resource_path),
        targets=post.targets,
        reading_time=post.reading_time,
        breadcrumbs=create_breadcrumbs_view_model(
            crumb=post.breadcrumbs,
            base_url=str(post.base_url),
        ),
        opengraph=create_opengraph_view_model(post.opengraph),
        article_opengraph=create_opengraph_article_view_model(post.article_opengraph),
    )


def create_blog_to_view_model(
    blog: Blog,
) -> ViewModelBlog:
    """Prepares the view model for the blog.

    Args:
        blog: The blog.
        base_url: The base URL of the site.

    Returns:
        The view model for the blog.
    """
    return ViewModelBlog(
        title=blog.title,
        base_url=blog.base_url,
        resource_path=blog.resource_path,
        targets=blog.targets,
        breadcrumbs=create_breadcrumbs_view_model(
            crumb=blog.breadcrumbs,
            base_url=str(blog.base_url),
        ),
        navigation=create_navigation_view_model(blog.navigation),
        posts=blog.posts.map(create_blogpost_view_model),
    )
