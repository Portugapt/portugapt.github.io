"""Tests for the blog view."""

from expression import Nothing, Some
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.unfold.components.breadcrumbs import (
    Breadcrumbs,
    ViewModelBreadcrumb,
    ViewModelBreadcrumbItem,
)
from electric_toolbox.unfold.components.opengraph import (
    Author,
    OpenGraph,
    OpenGraphArticle,
    ViewModelOpenGraph,
)
from electric_toolbox.unfold.sections.blog.models import BlogPost, ViewModelBlogPost
from electric_toolbox.unfold.sections.blog.view import prepare_blogpost_view_model


def test_prepare_blogpost_view_model() -> None:
    """Test prepare_blogpost_view_model."""
    base_url = 'https://example.com'
    post = BlogPost(
        title='Test Post',
        date='2023-01-01',
        contents='<h1>Test Post</h1>',
        base_url=HttpUrl(base_url),
        url=HttpUrl('https://example.com/blog/test-post'),
        reading_time='1 min',
        breadcrumbs=Breadcrumbs(
            path='test-post',
            title='Test Post',
            previous_crumb=Some(
                Breadcrumbs(
                    path='blog',
                    title='Blog',
                    previous_crumb=Some(
                        Breadcrumbs(
                            path='/',
                            title='Home',
                            previous_crumb=Nothing,
                        )
                    ),
                )
            ),
        ),
        opengraph=OpenGraph(
            title='Test Post',
            ogtype='article',
            image='https://example.com/image.jpg',
            url=HttpUrl('https://example.com/blog/test-post'),
            locale='en_US',
            description=Some('This is a test post.'),
            site_name=Some('Example Site'),
        ),
        article_opengraph=OpenGraphArticle(
            publication_time='2023-01-01T12:00:00',
            modified_time='2023-01-01T12:00:00',
            expiration_time='2025-01-01T12:00:00',
            authors=Block.of_seq(
                [
                    Author(
                        first_name='John',
                        last_name='Doe',
                        username='johndoe',
                        gender='male',
                        url=HttpUrl('https://example.com/author1'),
                    )
                ]
            ),
            section='Test Section',
            tags=Block.of_seq(['test', 'post']),
        ),
    )

    expected = ViewModelBlogPost(
        title='Test Post',
        date='2023-01-01',
        contents='<h1>Test Post</h1>',
        base_url='https://example.com/',
        url='https://example.com/blog/test-post',
        reading_time='1 min',
        breadcrumbs=ViewModelBreadcrumb(
            items=[
                ViewModelBreadcrumbItem(
                    name='Home',
                    url='https://example.com/',
                ),
                ViewModelBreadcrumbItem(
                    name='Blog',
                    url='https://example.com/blog',
                ),
                ViewModelBreadcrumbItem(
                    name='Test Post',
                    url='https://example.com/blog/test-post',
                ),
            ],
            json_ld='{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog"}, {"@type": "ListItem", "position": 3, "name": "Test Post", "item": "https://example.com/blog/test-post"}]}',  # noqa: E501
            show_root_item=True,
            separator='/',
        ),
        opengraph=ViewModelOpenGraph(
            parts=Block.of_seq(
                [
                    '<meta property="og:title" content="Test Post">',
                    '<meta property="og:type" content="article">',
                    '<meta property="og:image" content="https://example.com/image.jpg">',
                    '<meta property="og:url" content="https://example.com/blog/test-post">',
                    '<meta property="og:locale" content="en_US">',
                    '<meta property="og:description" content="This is a test post.">',
                    '<meta property="og:site_name" content="Example Site">',
                ]
            )
        ),
        article_opengraph=ViewModelOpenGraph(
            parts=Block.of_seq(
                [
                    '<meta property="og:article:published_time" content="2023-01-01T12:00:00">',
                    '<meta property="og:article:modified_time" content="2023-01-01T12:00:00">',
                    '<meta property="og:article:expiration_time" content="2025-01-01T12:00:00">',
                    '<meta property="og:article:section" content="Test Section">',
                    '<meta property="og:article:author" content="https://example.com/author1">',
                    '<meta property="og:article:tag" content="test">',
                    '<meta property="og:article:tag" content="post">',
                ]
            )
        ),
    )

    actual = prepare_blogpost_view_model(post)

    with open('test_prepare_blogpost_view_model.json', 'w') as f:
        f.write(actual.model_dump_json(indent=4))

    assert actual == expected
