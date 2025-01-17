"""Tests for navigation functions."""

from typing import Dict

import pytest
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.new.configs import (
    ReadFromPlural,
    Section,
)
from electric_toolbox.new.parsing.components.navigation import (
    NavigationMenu,
    NavigationSection,
    ViewModelNavigationMenu,
    create_navigation_menu,
    create_navigation_view_model,
)


@pytest.fixture
def sections() -> Dict[str, Section]:
    """Sample SiteConfigs for testing."""
    return {
        'blog': Section(
            title='Blog',
            description='My blog posts',
            resource_path='/blog',
            read_from=ReadFromPlural(
                type='plural',
                path='path/to/blog/posts',
                files=Block(),
            ),
        ),
        'about': Section(
            title='About',
            description='About me',
            resource_path='/about',
            read_from=ReadFromPlural(
                type='plural',
                path='path/to/about',
                files=Block(),
            ),
        ),
    }


def test_create_navigation_menu(sections: Dict[str, Section]) -> None:
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
    actual = create_navigation_menu(sections, base_url='https://example.com/')
    assert actual == expected


def test_create_navigation_menu_active_section(sections: Dict[str, Section]) -> None:
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
    actual = create_navigation_menu(sections, requester_section='Blog', base_url='https://example.com/')
    assert actual == expected


def test_create_navigation_view_model(sections: Dict[str, Section]) -> None:
    """Test create_navigation_view_model."""
    menu = create_navigation_menu(sections=sections, base_url='https://example.com/')
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
