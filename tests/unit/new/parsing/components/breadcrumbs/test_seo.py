"""Tests for the breadcrumbs BreadcrumbList JSON-LD."""

from expression import Nothing, Option, Some

from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs, to_json_ld


def _crumb(
    path: str,
    title: str,
    destination: str,
    extension: str = 'html',
    previous_crumb: Option[Breadcrumbs] = Nothing,
) -> Breadcrumbs:
    return Breadcrumbs(
        path=path,
        title=title,
        previous_crumb=previous_crumb,
        targets=TargetFiles(
            complete=Template(destination=destination, template=ExistingTemplates.BLOG_INDEX, extension=extension),
        ),
    )


def test_to_json_ld_empty_breadcrumbs() -> None:
    """An empty breadcrumb yields an empty itemListElement."""
    empty = _crumb('', 'Root', '', extension='')
    assert to_json_ld(crumb=empty) == {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [],
    }


def test_to_json_ld_single_level() -> None:
    """A single crumb produces one ListItem with an absolute item URL."""
    posts = _crumb('posts', 'Posts', 'posts')
    assert to_json_ld(crumb=posts, base_url='https://example.com') == {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Posts', 'item': 'https://example.com/posts.html'},
        ],
    }


def test_to_json_ld_multi_level() -> None:
    """Nested crumbs are emitted root-first with increasing positions."""
    posts = _crumb('posts', 'Posts', 'posts')
    article = _crumb('my-post', 'My Post', 'my-post', previous_crumb=Some(posts))
    assert to_json_ld(crumb=article, base_url='https://example.com') == {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Posts', 'item': 'https://example.com/posts.html'},
            {
                '@type': 'ListItem',
                'position': 2,
                'name': 'My Post',
                'item': 'https://example.com/posts/my-post.html',
            },
        ],
    }


def test_to_json_ld_no_base_url() -> None:
    """Without a base URL the item URLs are root-relative."""
    posts = _crumb('posts', 'Posts', 'posts')
    article = _crumb('my-post', 'My Post', 'my-post', previous_crumb=Some(posts))
    assert to_json_ld(crumb=article) == {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Posts', 'item': '/posts.html'},
            {'@type': 'ListItem', 'position': 2, 'name': 'My Post', 'item': '/posts/my-post.html'},
        ],
    }
