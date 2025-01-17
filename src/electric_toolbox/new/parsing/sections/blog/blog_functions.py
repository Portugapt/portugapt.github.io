"""Functions for parsing blog section."""

from typing import Any, Dict, Generator, Literal

from expression import Error, Option, Result, Some, effect
from expression.collections import Block
from expression.extra.result.traversable import traverse

from electric_toolbox.new.configs import FileData, ReadFromPlural, Section
from electric_toolbox.new.parsing.common import TargetFiles
from electric_toolbox.new.parsing.components.breadcrumbs import Breadcrumbs, generate_url
from electric_toolbox.new.parsing.components.navigation import NavigationMenu, create_navigation_menu

from .article_functions import read_post
from .models import Blog, BlogPost


@effect.result[Blog, Exception]()
def _read_blog(
    section: Section,
    breadcrumbs: Breadcrumbs,
    files: Block[FileData],
    base_url: str,
    navigation_menu: NavigationMenu,
) -> Generator[Any, Any, Blog]:
    """Read blog section.

    Args:
        section: The section to read.
        breadcrumbs: The breadcrumbs to use
        files: The files to read.
        base_url: The base url to use.
        navigation_menu: The navigation menu to use.

    Returns:
        The parsed blog.
    """

    def _curried_read_post(file: FileData) -> Result[BlogPost, Exception]:
        return read_post(file, Some(breadcrumbs), base_url)

    return Blog(
        title=section.title,
        base_url=base_url,
        resource_path=section.resource_path,
        breadcrumbs=breadcrumbs,
        targets=TargetFiles(
            complete=generate_url(breadcrumbs),
            hx=generate_url(breadcrumbs) + '_hx.html',
        ),
        posts=(yield from traverse(_curried_read_post, files)),
        navigation=navigation_menu,
    )


def read_blog(
    sections: Dict[str, Section],
    previous_crumb: Option[Breadcrumbs],
    base_url: str = '',
    section: Literal['blog'] = 'blog',
) -> Result[Blog, Exception]:
    """Read blog section.

    Args:
        sections: The sections.
        previous_crumb: The previous breadcrumb trail.
        base_url: The base URL.
        section: The section name.

    Returns:
        The parsed blog.
    """
    section_data = sections[section]
    breadcrumbs = Breadcrumbs(
        path=section_data.resource_path,
        title=section_data.title,
        previous_crumb=previous_crumb,
    )

    match section_data.read_from:
        case ReadFromPlural():
            return _read_blog(
                section=section_data,
                breadcrumbs=breadcrumbs,
                files=section_data.read_from.files,
                base_url=base_url,
                navigation_menu=create_navigation_menu(
                    sections=sections,
                    requester_section=section_data.title,
                    base_url=base_url,
                ),
            )

        case _:
            return Error(Exception(f'Unknown read_from type: {section_data.read_from}'))
