"""Tests for SEO function on breadcrumbs."""

from expression import Some

from electric_toolbox.new.parsing.components.breadcrumbs import Breadcrumbs, to_json_ld


def test_to_json_ld_empty_breadcrumbs() -> None:
    """Test JSON-LD generation for empty breadcrumbs."""
    breadcrumbs = Breadcrumbs(path='', title='Root')
    json_ld = to_json_ld(crumb=breadcrumbs)

    assert json_ld == {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [],
    }


def test_to_json_ld_single_level() -> None:
    """Test JSON-LD generation for a single-level breadcrumb."""
    breadcrumbs = Breadcrumbs(path='products', title='Products')
    json_ld = to_json_ld(crumb=breadcrumbs, base_url='https://example.com')

    assert json_ld == {
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


def test_to_json_ld_multi_level() -> None:
    """Test JSON-LD generation for multi-level breadcrumbs."""
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
    json_ld = to_json_ld(crumb=breadcrumbs, base_url='https://example.com')

    assert json_ld == {
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


def test_to_json_ld_with_full_url() -> None:
    """Test JSON-LD generation for breadcrumbs that have full URLs in the path."""
    breadcrumbs = Breadcrumbs(
        path='https://another.com/smartphones',
        title='Smartphones',
        previous_crumb=Some(
            Breadcrumbs(
                path='electronics',
                title='Electronics',
                previous_crumb=Some(Breadcrumbs(path='https://example.com/products', title='Products')),
            )
        ),
    )
    json_ld = to_json_ld(crumb=breadcrumbs, base_url='https://www.baseurl.com')

    assert json_ld == {
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
                'item': 'https://another.com/smartphones',
            },
        ],
    }


def test_to_json_ld_no_base_url() -> None:
    """Test JSON-LD generation when no base URL is provided."""
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
    json_ld = to_json_ld(crumb=breadcrumbs)  # No base_url provided

    assert json_ld == {
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
