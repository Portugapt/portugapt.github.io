"""Breadcrumbs tests for view functions."""

import json

from expression import Some

from electric_toolbox.new.parsing.components.breadcrumbs.models import Breadcrumbs, ViewModelBreadcrumbItem
from electric_toolbox.new.parsing.components.breadcrumbs.view import prepare_breadcrumbs_view_model


def test_prepare_breadcrumbs_view_model_empty_breadcrumbs() -> None:
    """Test prepare_breadcrumbs_view_model with empty breadcrumbs."""
    breadcrumbs = Breadcrumbs(path='', title='Root')
    view_model = prepare_breadcrumbs_view_model(breadcrumbs, base_url='')

    assert view_model.items == [ViewModelBreadcrumbItem(name='Root', url='/')]
    assert view_model.json_ld == json.dumps(
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [],
        }
    )


def test_prepare_breadcrumbs_view_model_single_level() -> None:
    """Test prepare_breadcrumbs_view_model with a single-level breadcrumb."""
    breadcrumbs = Breadcrumbs(path='products', title='Products')
    view_model = prepare_breadcrumbs_view_model(breadcrumbs, base_url='https://example.com')

    assert view_model.items == [ViewModelBreadcrumbItem(name='Products', url='https://example.com/products')]
    assert view_model.json_ld == json.dumps(
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {
                    '@type': 'ListItem',
                    'position': 1,
                    'name': 'Products',
                    'item': 'https://example.com/products',
                }
            ],
        }
    )


def test_prepare_breadcrumbs_view_model_multi_level() -> None:
    """Test prepare_breadcrumbs_view_model with multi-level breadcrumbs."""
    breadcrumbs = Breadcrumbs(
        path='smartphones',
        title='Smartphones',
        previous_crumb=Some(
            Breadcrumbs(
                path='electronics',
                title='Electronics',
                previous_crumb=Some(Breadcrumbs(path='products', title='Products')),
            )
        ),
    )
    view_model = prepare_breadcrumbs_view_model(breadcrumbs, base_url='https://example.com')

    assert view_model.items == [
        ViewModelBreadcrumbItem(name='Products', url='https://example.com/products'),
        ViewModelBreadcrumbItem(name='Electronics', url='https://example.com/products/electronics'),
        ViewModelBreadcrumbItem(
            name='Smartphones',
            url='https://example.com/products/electronics/smartphones',
        ),
    ]
    assert view_model.json_ld == json.dumps(
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {
                    '@type': 'ListItem',
                    'position': 1,
                    'name': 'Products',
                    'item': 'https://example.com/products',
                },
                {
                    '@type': 'ListItem',
                    'position': 2,
                    'name': 'Electronics',
                    'item': 'https://example.com/products/electronics',
                },
                {
                    '@type': 'ListItem',
                    'position': 3,
                    'name': 'Smartphones',
                    'item': 'https://example.com/products/electronics/smartphones',
                },
            ],
        }
    )


def test_prepare_breadcrumbs_view_model_no_base_url() -> None:
    """Test prepare_breadcrumbs_view_model when no base URL is provided."""
    breadcrumbs = Breadcrumbs(
        path='smartphones',
        title='Smartphones',
        previous_crumb=Some(
            Breadcrumbs(
                path='electronics',
                title='Electronics',
                previous_crumb=Some(Breadcrumbs(path='products', title='Products')),
            )
        ),
    )
    view_model = prepare_breadcrumbs_view_model(breadcrumbs, base_url='')

    assert view_model.items == [
        ViewModelBreadcrumbItem(name='Products', url='/products'),
        ViewModelBreadcrumbItem(name='Electronics', url='/products/electronics'),
        ViewModelBreadcrumbItem(name='Smartphones', url='/products/electronics/smartphones'),
    ]
    assert view_model.json_ld == json.dumps(
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {
                    '@type': 'ListItem',
                    'position': 1,
                    'name': 'Products',
                    'item': '/products',
                },
                {
                    '@type': 'ListItem',
                    'position': 2,
                    'name': 'Electronics',
                    'item': '/products/electronics',
                },
                {
                    '@type': 'ListItem',
                    'position': 3,
                    'name': 'Smartphones',
                    'item': '/products/electronics/smartphones',
                },
            ],
        }
    )


def test_prepare_breadcrumbs_view_model_hide_root_item() -> None:
    """Test prepare_breadcrumbs_view_model with show_root_item=False."""
    breadcrumbs = Breadcrumbs(
        path='smartphones',
        title='Smartphones',
        previous_crumb=Some(
            Breadcrumbs(
                path='electronics',
                title='Electronics',
                previous_crumb=Some(Breadcrumbs(path='products', title='Products')),
            )
        ),
    )
    view_model = prepare_breadcrumbs_view_model(breadcrumbs, base_url='https://example.com', show_root_item=False)

    assert view_model.items == [
        ViewModelBreadcrumbItem(name='Electronics', url='https://example.com/products/electronics'),
        ViewModelBreadcrumbItem(
            name='Smartphones',
            url='https://example.com/products/electronics/smartphones',
        ),
    ]
    assert view_model.json_ld == json.dumps(
        {
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {
                    '@type': 'ListItem',
                    'position': 1,
                    'name': 'Products',
                    'item': 'https://example.com/products',
                },
                {
                    '@type': 'ListItem',
                    'position': 2,
                    'name': 'Electronics',
                    'item': 'https://example.com/products/electronics',
                },
                {
                    '@type': 'ListItem',
                    'position': 3,
                    'name': 'Smartphones',
                    'item': 'https://example.com/products/electronics/smartphones',
                },
            ],
        }
    )
