"""Tests for the blog view models.

Rather than snapshotting the whole structure, these assert the transformations
the view layer is responsible for: Option wrapping, the merged Open Graph parts,
the derived byline/tags, the collected filter tags and the pass-through of the
pre-rendered SEO bundle.
"""

from expression import Nothing, Option, Some
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing.common import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs
from electric_toolbox.parsing.components.navigation import NavigationMenu
from electric_toolbox.parsing.components.opengraph import Author, OpenGraph, OpenGraphArticle
from electric_toolbox.parsing.components.seo import HeadMeta
from electric_toolbox.parsing.sections.blog.models import Blog, BlogPost
from electric_toolbox.parsing.sections.blog.view import create_blog_to_view_model, create_blogpost_view_model


def _targets(destination: str, complete: ExistingTemplates, hx: ExistingTemplates) -> TargetFiles:
    return TargetFiles(
        complete=Template(destination=destination, template=complete, extension='html'),
        hx=Template(destination=destination + '_hx', template=hx, extension='html'),
    )


def _post(  # noqa: PLR0913
    *,
    title: str,
    slug: str,
    tags: list[str],
    authors: list[Author],
    thumbnail: Option[str] = Nothing,
    blog_crumb: Breadcrumbs,
) -> BlogPost:
    crumb = Breadcrumbs(
        path=slug,
        title=title,
        targets=_targets(slug, ExistingTemplates.BLOG_ARTICLE, ExistingTemplates.BLOG_ARTICLE_HX),
        previous_crumb=Some(blog_crumb),
    )
    return BlogPost(
        title=title,
        date='2023-01-01T00:00:00',
        thumbnail=thumbnail,
        base_url=HttpUrl('https://example.com'),
        resource_path=f'/blog_hx/{slug}.html',
        url=f'https://example.com/blog/{slug}.html',
        targets=_targets(slug, ExistingTemplates.BLOG_ARTICLE, ExistingTemplates.BLOG_ARTICLE_HX),
        contents=f'<h1>{title}</h1>',
        reading_time='1 min',
        breadcrumbs=crumb,
        opengraph=OpenGraph(
            title=title,
            ogtype='article',
            image='https://example.com/i.jpg',
            url=HttpUrl(f'https://example.com/blog/{slug}.html'),
            locale='en',
            description=Some('A summary.'),
        ),
        article_opengraph=OpenGraphArticle(
            publication_time='2023-01-01T00:00:00',
            modified_time='2023-01-01T00:00:00',
            expiration_time='2025-01-01T00:00:00',
            authors=Block.of_seq(authors),
            section='Tech',
            tags=Block.of_seq(tags),
        ),
        summary=Some('A summary.'),
        seo=HeadMeta(parts=Block.of_seq(['<link rel="canonical" href="x">'])),
    )


def _blog_crumb() -> Breadcrumbs:
    return Breadcrumbs(
        path='blog',
        title='Blog',
        targets=_targets('blog', ExistingTemplates.BLOG_INDEX, ExistingTemplates.BLOG_INDEX_HX),
    )


def test_create_blogpost_view_model_transformations() -> None:
    """A post view model wraps options, merges OG parts and derives byline/tags."""
    author = Author(first_name='John', last_name='Doe', username='jd', url=HttpUrl('https://example.com/jd'))
    post = _post(
        title='Post 1',
        slug='post-1',
        tags=['tech', 'fp'],
        authors=[author],
        thumbnail=Some('t.jpg'),
        blog_crumb=_blog_crumb(),
    )

    vm = create_blogpost_view_model(post)

    assert vm.thumbnail == Some('t.jpg')
    assert vm.base_url == 'https://example.com/'
    assert vm.byline == 'John Doe'
    assert vm.tags == Block.of_seq(['tech', 'fp'])
    assert vm.summary == Some('A summary.')
    assert vm.seo == post.seo
    # The page + article Open Graph parts are merged into one block.
    assert '<meta property="og:title" content="Post 1">' in vm.opengraph.parts
    assert '<meta property="og:article:tag" content="tech">' in vm.opengraph.parts
    assert [item.name for item in vm.breadcrumbs.items] == ['Blog', 'Post 1']


def test_create_blog_to_view_model_collects_tags() -> None:
    """The blog view model collects unique filter tags with their fragment URLs."""
    blog_crumb = _blog_crumb()
    blog = Blog(
        title='Test Blog',
        base_url='https://example.com/',
        resource_path='blog',
        targets=_targets('blog', ExistingTemplates.BLOG_INDEX, ExistingTemplates.BLOG_INDEX_HX),
        breadcrumbs=blog_crumb,
        navigation=NavigationMenu(sections=Block.empty()),
        opengraph=OpenGraph(
            title='Test Blog',
            ogtype='website',
            image='https://example.com/og.png',
            url=HttpUrl('https://example.com'),
            locale='en_US',
        ),
        posts=Block.of_seq(
            [
                _post(title='Post 1', slug='post-1', tags=['tech', 'fp'], authors=[], blog_crumb=blog_crumb),
                _post(title='Post 2', slug='post-2', tags=['tech'], authors=[], blog_crumb=blog_crumb),
            ]
        ),
    )

    vm = create_blog_to_view_model(blog)

    assert len(vm.posts) == 2
    assert vm.all_hx_get == '/blog_hx.html'
    assert vm.all_push_url == '/blog.html'

    tags = {tag.name: tag for tag in vm.tags}
    assert set(tags) == {'tech', 'fp'}
    assert tags['tech'].count == 2
    assert tags['fp'].count == 1
    assert tags['tech'].hx_get == '/blog_hx/tag/tech.html'
    assert tags['tech'].push_url == '/blog.html?tag=tech'
