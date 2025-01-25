"""Functions for the navigation component."""

from typing import Dict

from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.configs import Section

from .models import NavigationMenu, NavigationSection, ViewModelNavigationMenu


def create_navigation_menu(
    sections: Dict[str, Section],
    requester_section: str = '',
    base_url: str = '',
) -> NavigationMenu:
    """Creates a NavigationMenu from SiteConfigs.

    Args:
        sections: The sections of the site.
        requester_section: The section that is requesting the navigation menu.
        base_url: The base URL of the site.

    Returns:
        A NavigationMenu object.
    """

    def _navigation_section(section: Section, base_url: str) -> NavigationSection:
        return NavigationSection(
            title=section.title,
            base_url=HttpUrl(base_url),
            path=f'{section.resource_path}.html',
            hx_get=f'{section.resource_path}_hx.html',
            active=True if section.title == requester_section else False,
        )

    _built_sections = Block.of_seq(
        _navigation_section(
            section=section,
            base_url=base_url,
        )
        for _, section in sections.items()
    )

    return NavigationMenu(sections=_built_sections)


def create_navigation_view_model(menu: NavigationMenu) -> ViewModelNavigationMenu:
    """Creates a ViewModelNavigationMenu from a NavigationMenu.

    Args:
        menu: The NavigationMenu object.

    Returns:
        A ViewModelNavigationMenu object.
    """
    return ViewModelNavigationMenu(sections=menu.sections)
