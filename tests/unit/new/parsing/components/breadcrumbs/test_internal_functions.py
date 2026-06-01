"""Tests for the breadcrumbs internal URL helpers.

URLs are derived from each crumb's ``targets`` (destination + extension), not
from ``path``; these tests exercise that current contract.
"""

from expression import Nothing, Option, Some

from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import (
    Breadcrumbs,
    block_of_paths,
    generate_url,
    get_push_url,
)


def _crumb(
    path: str,
    title: str,
    destination: str,
    extension: str = 'html',
    previous_crumb: Option[Breadcrumbs] = Nothing,
) -> Breadcrumbs:
    """Build a breadcrumb the way the real parsing code does (with a target)."""
    return Breadcrumbs(
        path=path,
        title=title,
        previous_crumb=previous_crumb,
        targets=TargetFiles(
            complete=Template(destination=destination, template=ExistingTemplates.BLOG_INDEX, extension=extension),
        ),
    )


def test_block_of_paths_single_segment() -> None:
    """A root crumb yields a single segment from its destination."""
    posts = _crumb('posts', 'Posts', 'posts')
    assert [part.push for part in block_of_paths(posts)] == ['posts']


def test_block_of_paths_multiple_segments() -> None:
    """A nested crumb accumulates segments from root to current."""
    posts = _crumb('posts', 'Posts', 'posts')
    article = _crumb('my-post', 'My Post', 'my-post', previous_crumb=Some(posts))
    assert [part.push for part in block_of_paths(article)] == ['posts', 'my-post']


def test_block_of_paths_empty_path() -> None:
    """An empty path produces no segments."""
    empty = _crumb('', 'Empty', '', extension='')
    assert len(block_of_paths(empty)) == 0


def test_generate_url_single_segment() -> None:
    """A root crumb resolves to its destination plus extension."""
    posts = _crumb('posts', 'Posts', 'posts')
    assert generate_url(posts) == '/posts.html'


def test_generate_url_multiple_segments() -> None:
    """Nested crumbs join their destinations; only the leaf carries the extension."""
    posts = _crumb('posts', 'Posts', 'posts')
    article = _crumb('my-post', 'My Post', 'my-post', previous_crumb=Some(posts))
    assert generate_url(article) == '/posts/my-post.html'
    assert generate_url(article, base_url='https://example.com') == 'https://example.com/posts/my-post.html'


def test_generate_url_empty_path() -> None:
    """An empty breadcrumb resolves to the site root."""
    empty = _crumb('', 'Empty', '', extension='')
    assert generate_url(empty) == '/'
    assert generate_url(empty, base_url='https://example.com') == 'https://example.com/'


def test_get_push_url() -> None:
    """The push URL is the root-relative href used by hx-boost links."""
    posts = _crumb('posts', 'Posts', 'posts')
    article = _crumb('my-post', 'My Post', 'my-post', previous_crumb=Some(posts))
    assert get_push_url(article, base_url='') == '/posts/my-post.html'
