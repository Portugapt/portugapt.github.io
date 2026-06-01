"""Views for the blog."""

from expression.collections import Block
from slugify import slugify

from electric_toolbox.parsing.components.breadcrumbs import create_breadcrumbs_view_model
from electric_toolbox.parsing.components.navigation import create_navigation_view_model
from electric_toolbox.parsing.components.opengraph import (
    ViewModelOpenGraph,
    create_opengraph_article_view_model,
    create_opengraph_view_model,
)

from .models import Blog, BlogPost, ViewModelBlog, ViewModelBlogPost, ViewModelTag


def _byline(post: BlogPost) -> str:
    """Comma-joined author names for the article header."""
    return ', '.join(f'{a.first_name} {a.last_name}'.strip() for a in post.article_opengraph.authors)


def _collect_tags(blog: Blog) -> Block[ViewModelTag]:
    """Builds the unique, ordered tag list used by the filter bar.

    Each tag is a plain ``/<resource>.html?tag=<slug>`` link. Filtering happens
    client-side (the page already carries every post), and the query survives a
    refresh because the static document is served regardless of the query string.
    """
    counts: dict[str, int] = {}
    order: list[str] = []
    for post in blog.posts:
        for tag in post.article_opengraph.tags:
            if tag not in counts:
                counts[tag] = 0
                order.append(tag)
            counts[tag] += 1
    return Block.of_seq(
        ViewModelTag(
            name=tag,
            slug=slugify(tag),
            href=f'/{blog.resource_path}.html?tag={slugify(tag)}',
            count=counts[tag],
        )
        for tag in order
    )


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
        summary=post.summary,
        seo=post.seo,
        byline=_byline(post),
        tags=post.article_opengraph.tags,
        tag_slugs=post.article_opengraph.tags.map(slugify),
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
        seo=blog.seo,
        tags=_collect_tags(blog),
        all_href=f'/{blog.resource_path}.html',
    )
