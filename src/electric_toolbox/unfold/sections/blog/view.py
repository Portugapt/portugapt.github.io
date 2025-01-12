"""Views for the blog."""

from electric_toolbox.unfold.components.breadcrumbs import prepare_breadcrumbs_view_model
from electric_toolbox.unfold.components.opengraph import article_og_to_view_model, page_og_to_view_model

from .models import BlogPost, ViewModelBlogPost


def prepare_blogpost_view_model(
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
        url=str(post.url),
        reading_time=post.reading_time,
        breadcrumbs=prepare_breadcrumbs_view_model(
            crumb=post.breadcrumbs,
            base_url=str(post.base_url),
        ),
        opengraph=page_og_to_view_model(post.opengraph),
        article_opengraph=article_og_to_view_model(post.article_opengraph),
    )
