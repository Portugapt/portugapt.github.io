"""Tests for the blog view."""

from expression import Nothing, Some
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing.common import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import (
    Breadcrumbs,
    ViewModelBreadcrumb,
    ViewModelBreadcrumbItem,
)
from electric_toolbox.parsing.components.navigation import (
    NavigationMenu,
    NavigationSection,
    ViewModelNavigationMenu,
)
from electric_toolbox.parsing.components.opengraph import (
    Author,
    OpenGraph,
    OpenGraphArticle,
    ViewModelOpenGraph,
)
from electric_toolbox.parsing.sections.blog.models import Blog, BlogPost, ViewModelBlog, ViewModelBlogPost
from electric_toolbox.parsing.sections.blog.view import create_blog_to_view_model, create_blogpost_view_model


def test_prepare_blogpost_view_model() -> None:
    """Test prepare_blogpost_view_model."""
    base_url = 'https://example.com'
    post = BlogPost(
        title='Test Post',
        date='2023-01-01',
        contents='<h1>Test Post</h1>',
        thumbnail='test.jpg',
        base_url=HttpUrl(base_url),
        resource_path='blog/test-post',
        targets=TargetFiles(
            complete=Template(
                destination='blog/test-post',
                template=ExistingTemplates.BLOG_ARTICLE,
                extension='html',
            ),
            hx=Template(
                destination='blog/test-post/hx',
                template=ExistingTemplates.BLOG_ARTICLE_HX,
                extension='html',
            ),
        ),
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
        thumbnail=Some('test.jpg'),
        base_url='https://example.com/',
        resource_path='blog/test-post',
        targets=TargetFiles(
            complete=Template(
                destination='blog/test-post',
                template=ExistingTemplates.BLOG_ARTICLE,
                extension='html',
            ),
            hx=Template(
                destination='blog/test-post/hx',
                template=ExistingTemplates.BLOG_ARTICLE_HX,
                extension='html',
            ),
        ),
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

    actual = create_blogpost_view_model(post)

    assert actual == expected


def test_create_blog_to_view_model() -> None:
    """Test create_blog_to_view_model."""
    blog = Blog(
        title='Test Blog',
        base_url='https://example.com/',
        resource_path='/blog',
        targets=TargetFiles(
            complete=Template(
                destination='blog',
                template=ExistingTemplates.BLOG_INDEX,
                extension='html',
            ),
            hx=Template(
                destination='blog_hx',
                template=ExistingTemplates.BLOG_INDEX_HX,
                extension='html',
            ),
        ),
        breadcrumbs=Breadcrumbs(
            path='/blog',
            title='Blog',
            previous_crumb=Some(
                Breadcrumbs(
                    path='/',
                    title='Home',
                )
            ),
        ),
        navigation=NavigationMenu(
            sections=Block.of_seq(
                [
                    NavigationSection(
                        title='Home',
                        base_url=HttpUrl('https://example.com/'),
                        path='/',
                        hx_get='/_hx.html',
                    ),
                    NavigationSection(
                        title='Blog',
                        base_url=HttpUrl('https://example.com/'),
                        path='/blog',
                        hx_get='/blog_hx.html',
                        active=True,
                    ),
                ]
            )
        ),
        posts=Block.of_seq(
            [
                BlogPost(
                    title='Post 1',
                    date='2023-01-01',
                    contents='<h1>Post 1</h1>',
                    reading_time='5 min',
                    base_url=HttpUrl('https://example.com/'),
                    resource_path='blog/post-1',
                    targets=TargetFiles(
                        complete=Template(
                            destination='blog/post_1',
                            template=ExistingTemplates.BLOG_ARTICLE,
                            extension='html',
                        ),
                        hx=Template(
                            destination='blog/post-1/hx',
                            template=ExistingTemplates.BLOG_ARTICLE_HX,
                            extension='html',
                        ),
                    ),
                    breadcrumbs=Breadcrumbs(
                        path='post-1',
                        title='Post 1',
                        previous_crumb=Some(
                            Breadcrumbs(
                                path='blog',
                                title='Blog',
                                previous_crumb=Some(
                                    Breadcrumbs(
                                        path='/',
                                        title='Home',
                                    )
                                ),
                            )
                        ),
                    ),
                    opengraph=OpenGraph(
                        title='Post 1',
                        ogtype='article',
                        image='https://example.com/image1.jpg',
                        url=HttpUrl('https://example.com/blog/post-1'),
                        locale='en_US',
                    ),
                    article_opengraph=OpenGraphArticle(
                        publication_time='2023-01-01T00:00:00',
                        modified_time='2023-01-01T00:00:00',
                        expiration_time='2025-01-01T00:00:00',
                        authors=Block.empty(),
                        section='Test Section',
                        tags=Block.empty(),
                    ),
                ),
                BlogPost(
                    title='Post 2',
                    date='2023-01-15',
                    contents='<h1>Post 2</h1>',
                    reading_time='10 min',
                    base_url=HttpUrl('https://example.com/'),
                    resource_path='blog/post-2',
                    targets=TargetFiles(
                        complete=Template(
                            destination='blog/post_2',
                            template=ExistingTemplates.BLOG_ARTICLE,
                            extension='html',
                        ),
                        hx=Template(
                            destination='blog/post-2/hx',
                            template=ExistingTemplates.BLOG_ARTICLE_HX,
                            extension='html',
                        ),
                    ),
                    breadcrumbs=Breadcrumbs(
                        path='post-2',
                        title='Post 2',
                        previous_crumb=Some(
                            Breadcrumbs(
                                path='blog',
                                title='Blog',
                                previous_crumb=Some(
                                    Breadcrumbs(
                                        path='/',
                                        title='Home',
                                    )
                                ),
                            )
                        ),
                    ),
                    opengraph=OpenGraph(
                        title='Post 2',
                        ogtype='article',
                        image='https://example.com/image2.jpg',
                        url=HttpUrl('https://example.com/blog/post-2'),
                        locale='en_US',
                    ),
                    article_opengraph=OpenGraphArticle(
                        publication_time='2023-01-15T00:00:00',
                        modified_time='2023-01-15T00:00:00',
                        expiration_time='2025-01-15T00:00:00',
                        authors=Block.empty(),
                        section='Test Section',
                        tags=Block.empty(),
                    ),
                ),
            ]
        ),
    )

    expected = ViewModelBlog(
        title='Test Blog',
        base_url='https://example.com/',
        resource_path='/blog',
        targets=TargetFiles(
            complete=Template(
                destination='blog',
                template=ExistingTemplates.BLOG_INDEX,
                extension='html',
            ),
            hx=Template(
                destination='blog_hx',
                template=ExistingTemplates.BLOG_INDEX_HX,
                extension='html',
            ),
        ),
        breadcrumbs=ViewModelBreadcrumb(
            items=[
                ViewModelBreadcrumbItem(name='Home', url='https://example.com/'),
                ViewModelBreadcrumbItem(name='Blog', url='https://example.com/blog'),
            ],
            json_ld='{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog"}]}',  # noqa: E501
            show_root_item=True,
            separator='/',
        ),
        navigation=ViewModelNavigationMenu(
            sections=Block.of_seq(
                [
                    NavigationSection(
                        title='Home',
                        base_url=HttpUrl('https://example.com/'),
                        path='/',
                        hx_get='/_hx.html',
                    ),
                    NavigationSection(
                        title='Blog',
                        base_url=HttpUrl('https://example.com/'),
                        path='/blog',
                        hx_get='/blog_hx.html',
                        active=True,
                    ),
                ]
            )
        ),
        posts=Block.of_seq(
            [
                ViewModelBlogPost(
                    title='Post 1',
                    date='2023-01-01',
                    contents='<h1>Post 1</h1>',
                    reading_time='5 min',
                    base_url='https://example.com/',
                    resource_path='blog/post-1',
                    targets=TargetFiles(
                        complete=Template(
                            destination='blog/post_1',
                            template=ExistingTemplates.BLOG_ARTICLE,
                            extension='html',
                        ),
                        hx=Template(
                            destination='blog/post-1/hx',
                            template=ExistingTemplates.BLOG_ARTICLE_HX,
                            extension='html',
                        ),
                    ),
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
                                name='Post 1',
                                url='https://example.com/blog/post-1',
                            ),
                        ],
                        json_ld='{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog"}, {"@type": "ListItem", "position": 3, "name": "Post 1", "item": "https://example.com/blog/post-1"}]}',  # noqa: E501
                        show_root_item=True,
                        separator='/',
                    ),
                    opengraph=ViewModelOpenGraph(
                        parts=Block.of_seq(
                            [
                                '<meta property="og:title" content="Post 1">',
                                '<meta property="og:type" content="article">',
                                '<meta property="og:image" content="https://example.com/image1.jpg">',
                                '<meta property="og:url" content="https://example.com/blog/post-1">',
                                '<meta property="og:locale" content="en_US">',
                            ]
                        )
                    ),
                    article_opengraph=ViewModelOpenGraph(
                        parts=Block.of_seq(
                            [
                                '<meta property="og:article:published_time" content="2023-01-01T00:00:00">',
                                '<meta property="og:article:modified_time" content="2023-01-01T00:00:00">',
                                '<meta property="og:article:expiration_time" content="2025-01-01T00:00:00">',
                                '<meta property="og:article:section" content="Test Section">',
                            ]
                        )
                    ),
                ),
                ViewModelBlogPost(
                    title='Post 2',
                    date='2023-01-15',
                    contents='<h1>Post 2</h1>',
                    reading_time='10 min',
                    base_url='https://example.com/',
                    resource_path='blog/post-2',
                    targets=TargetFiles(
                        complete=Template(
                            destination='blog/post_2',
                            template=ExistingTemplates.BLOG_ARTICLE,
                            extension='html',
                        ),
                        hx=Template(
                            destination='blog/post-2/hx',
                            template=ExistingTemplates.BLOG_ARTICLE_HX,
                            extension='html',
                        ),
                    ),
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
                                name='Post 2',
                                url='https://example.com/blog/post-2',
                            ),
                        ],
                        json_ld='{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"}, {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog"}, {"@type": "ListItem", "position": 3, "name": "Post 2", "item": "https://example.com/blog/post-2"}]}',  # noqa: E501
                        show_root_item=True,
                        separator='/',
                    ),
                    opengraph=ViewModelOpenGraph(
                        parts=Block.of_seq(
                            [
                                '<meta property="og:title" content="Post 2">',
                                '<meta property="og:type" content="article">',
                                '<meta property="og:image" content="https://example.com/image2.jpg">',
                                '<meta property="og:url" content="https://example.com/blog/post-2">',
                                '<meta property="og:locale" content="en_US">',
                            ]
                        )
                    ),
                    article_opengraph=ViewModelOpenGraph(
                        parts=Block.of_seq(
                            [
                                '<meta property="og:article:published_time" content="2023-01-15T00:00:00">',
                                '<meta property="og:article:modified_time" content="2023-01-15T00:00:00">',
                                '<meta property="og:article:expiration_time" content="2025-01-15T00:00:00">',
                                '<meta property="og:article:section" content="Test Section">',
                            ]
                        )
                    ),
                ),
            ]
        ),
    )

    actual = create_blog_to_view_model(blog)

    assert actual == expected
