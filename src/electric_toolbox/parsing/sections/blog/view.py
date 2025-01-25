"""Views for the blog."""

from expression.collections import Block

from electric_toolbox.parsing.components.breadcrumbs import create_breadcrumbs_view_model
from electric_toolbox.parsing.components.navigation import create_navigation_view_model
from electric_toolbox.parsing.components.opengraph import (
    ViewModelOpenGraph,
    create_opengraph_article_view_model,
    create_opengraph_view_model,
)

from .models import Blog, BlogPost, ViewModelBlog, ViewModelBlogPost


def _join_opengraph_views(
    opengraph_views: Block[ViewModelOpenGraph],
) -> ViewModelOpenGraph:
    """Joins the opengraph views into a single view model.

    Args:
        opengraph_views: The opengraph views.

    Returns:
        The joined view model.
    """

    def _accumulate(
        state: Block[str],
        view: ViewModelOpenGraph,
    ) -> Block[str]:
        return state.append(view.parts)

    return ViewModelOpenGraph(parts=opengraph_views.fold(_accumulate, Block.empty()))


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
        thumbnail=post.thumbnail,
        base_url=str(post.base_url),
        resource_path=str(post.resource_path),
        url=str(post.url),
        targets=post.targets,
        reading_time=post.reading_time,
        breadcrumbs=create_breadcrumbs_view_model(
            crumb=post.breadcrumbs,
            base_url=str(post.base_url),
        ),
        opengraph=_join_opengraph_views(
            opengraph_views=Block.of(
                create_opengraph_view_model(post.opengraph), create_opengraph_article_view_model(post.article_opengraph)
            )
        ),
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
        opengraph=create_opengraph_view_model(blog.opengraph),
    )
