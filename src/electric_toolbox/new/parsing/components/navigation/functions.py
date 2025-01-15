"""Functions for the navigation component."""

from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.new.configs import Section, SiteConfigs

from .models import NavigationMenu, NavigationSection, ViewModelNavigationMenu


def create_navigation_menu(
    configs: SiteConfigs,
    requester_section: str = '',
) -> NavigationMenu:
    """Creates a NavigationMenu from SiteConfigs.

    Args:
        configs: The SiteConfigs object.
        requester_section: The section that is requesting the menu.

    Returns:
        A NavigationMenu object.
    """

    def _navigation_section(configs: SiteConfigs, section: Section) -> NavigationSection:
        return NavigationSection(
            title=section.title,
            base_url=HttpUrl(configs.base_url),
            path=section.url,
            hx_get=f'{section.url}_hx.html',
            active=True if section.title == requester_section else False,
        )

    sections = Block.of_seq(
        _navigation_section(
            configs=configs,
            section=section,
        )
        for _, section in configs.sections.items()
    )

    return NavigationMenu(sections=sections)


def create_navigation_view_model(menu: NavigationMenu) -> ViewModelNavigationMenu:
    """Creates a ViewModelNavigationMenu from a NavigationMenu.

    Args:
        menu: The NavigationMenu object.

    Returns:
        A ViewModelNavigationMenu object.
    """
    return ViewModelNavigationMenu(sections=menu.sections)
