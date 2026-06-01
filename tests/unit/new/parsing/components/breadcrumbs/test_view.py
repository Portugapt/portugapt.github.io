"""Tests for the breadcrumbs view model."""

import json

from expression import Nothing, Option, Some

from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs.models import Breadcrumbs, ViewModelBreadcrumbItem
from electric_toolbox.parsing.components.breadcrumbs.view import create_breadcrumbs_view_model


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


def test_view_model_single_level() -> None:
    """A root crumb yields one item carrying href + canonical URLs."""
    view_model = create_breadcrumbs_view_model(_crumb('posts', 'Posts', 'posts'), base_url='https://example.com')

    assert view_model.items == [
        ViewModelBreadcrumbItem(
            name='Posts',
            url='https://example.com/posts.html',
            push_url='/posts.html',
        )
    ]


def test_view_model_multi_level() -> None:
    """Nested crumbs are ordered root-first, each with its own URLs + JSON-LD."""
    posts = _crumb('posts', 'Posts', 'posts')
    article = _crumb('my-post', 'My Post', 'my-post', previous_crumb=Some(posts))
    view_model = create_breadcrumbs_view_model(article, base_url='https://example.com')

    assert view_model.items == [
        ViewModelBreadcrumbItem(
            name='Posts',
            url='https://example.com/posts.html',
            push_url='/posts.html',
        ),
        ViewModelBreadcrumbItem(
            name='My Post',
            url='https://example.com/posts/my-post.html',
            push_url='/posts/my-post.html',
        ),
    ]
    assert view_model.json_ld == json.dumps(
        {
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
    )


def test_view_model_hide_root_item() -> None:
    """show_root_item=False drops the first crumb from the rendered items."""
    posts = _crumb('posts', 'Posts', 'posts')
    article = _crumb('my-post', 'My Post', 'my-post', previous_crumb=Some(posts))
    view_model = create_breadcrumbs_view_model(article, base_url='https://example.com', show_root_item=False)

    assert view_model.items == [
        ViewModelBreadcrumbItem(
            name='My Post',
            url='https://example.com/posts/my-post.html',
            push_url='/posts/my-post.html',
        ),
    ]
