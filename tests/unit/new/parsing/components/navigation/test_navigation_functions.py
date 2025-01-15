"""Tests for navigation functions."""

import pytest
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.new.configs import (
    ConfigSettings,
    ReadFromPlural,
    Section,
    SiteConfigs,
)
from electric_toolbox.new.parsing.components.navigation import (
    NavigationMenu,
    NavigationSection,
    ViewModelNavigationMenu,
    create_navigation_menu,
    create_navigation_view_model,
)


@pytest.fixture
def site_configs() -> SiteConfigs:
    """Sample SiteConfigs for testing."""
    return SiteConfigs(
        settings=ConfigSettings(
            include_drafts=True,
        ),
        base_url='https://example.com',
        website_name='My Website',
        sections={
            'blog': Section(
                title='Blog',
                description='My blog posts',
                url='/blog',
                read_from=ReadFromPlural(
                    type='plural',
                    path='path/to/blog/posts',
                    files=Block(),
                ),
            ),
            'about': Section(
                title='About',
                description='About me',
                url='/about',
                read_from=ReadFromPlural(
                    type='plural',
                    path='path/to/about',
                    files=Block(),
                ),
            ),
        },
    )


def test_create_navigation_menu(site_configs: SiteConfigs) -> None:
    """Test create_navigation_menu."""
    expected = NavigationMenu(
        sections=Block.of_seq(
            [
                NavigationSection(
                    title='Blog',
                    base_url=HttpUrl('https://example.com/'),
                    path='/blog',
                    hx_get='/blog_hx.html',
                    active=False,
                ),
                NavigationSection(
                    title='About',
                    base_url=HttpUrl('https://example.com/'),
                    path='/about',
                    hx_get='/about_hx.html',
                    active=False,
                ),
            ]
        )
    )
    actual = create_navigation_menu(site_configs)
    assert actual == expected


def test_create_navigation_menu_active_section(site_configs: SiteConfigs) -> None:
    """Test create_navigation_menu with an active section."""
    expected = NavigationMenu(
        sections=Block.of_seq(
            [
                NavigationSection(
                    title='Blog',
                    base_url=HttpUrl('https://example.com/'),
                    path='/blog',
                    hx_get='/blog_hx.html',
                    active=True,  # Blog is active
                ),
                NavigationSection(
                    title='About',
                    base_url=HttpUrl('https://example.com/'),
                    path='/about',
                    hx_get='/about_hx.html',
                    active=False,
                ),
            ]
        )
    )
    actual = create_navigation_menu(site_configs, requester_section='Blog')
    assert actual == expected


def test_create_navigation_view_model(site_configs: SiteConfigs) -> None:
    """Test create_navigation_view_model."""
    menu = create_navigation_menu(site_configs)
    expected = ViewModelNavigationMenu(
        sections=Block.of_seq(
            [
                NavigationSection(
                    title='Blog',
                    base_url=HttpUrl('https://example.com/'),
                    path='/blog',
                    hx_get='/blog_hx.html',
                    active=False,
                ),
                NavigationSection(
                    title='About',
                    base_url=HttpUrl('https://example.com/'),
                    path='/about',
                    hx_get='/about_hx.html',
                    active=False,
                ),
            ]
        )
    )
    actual = create_navigation_view_model(menu)
    assert actual == expected
