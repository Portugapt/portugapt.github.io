"""Functions for parsing blog section."""

from typing import Any, Dict, Generator, Literal

from expression import Error, Result, Some, effect
from expression.collections import Block
from expression.extra.result.traversable import traverse

from electric_toolbox.configs import FileData, ReadFromPlural, Section, WebsiteInfo
from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing.common import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs, get_hx_url, get_push_url
from electric_toolbox.parsing.components.navigation import NavigationMenu, create_navigation_menu
from electric_toolbox.parsing.components.opengraph import create_opengraph_typed_website

from .article_functions import read_post
from .models import Blog, BlogPost


@effect.result[Blog, Exception]()
def _read_blog(
    section: Section,
    breadcrumbs: Breadcrumbs,
    website_info: WebsiteInfo,
    files: Block[FileData],
    base_url: str,
    navigation_menu: NavigationMenu,
) -> Generator[Any, Any, Blog]:
    """Read blog section.

    Args:
        section: The section to read.
        breadcrumbs: The breadcrumbs to use.
        website_info: The website info to use.
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
            complete=Template(
                destination=get_push_url(crumb=breadcrumbs, base_url=''),
                template=breadcrumbs.targets.complete.template,
                extension=breadcrumbs.targets.complete.extension,
            ),
            hx=Template(
                destination=get_hx_url(crumb=breadcrumbs),
                template=breadcrumbs.targets.hx.template,
                extension=breadcrumbs.targets.hx.extension,
            ),
        ),
        posts=(yield from traverse(_curried_read_post, files)),
        navigation=navigation_menu,
        opengraph=(
            yield from create_opengraph_typed_website(
                title=website_info.title,
                description=website_info.description,
                image=website_info.image,
                locale=website_info.locale,
                url=base_url,
            )
        ),
    )


def read_blog(
    sections: Dict[str, Section],
    website_info: WebsiteInfo,
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
    targets = TargetFiles(
        complete=Template(
            destination=section_data.resource_path,
            template=ExistingTemplates.BLOG_INDEX,
            extension='html',
        ),
        hx=Template(
            destination=section_data.resource_path + '_hx',
            template=ExistingTemplates.BLOG_INDEX_HX,
            extension='html',
        ),
    )
    breadcrumbs = Breadcrumbs(
        path=section_data.resource_path,
        title=section_data.title,
        targets=targets,
    )

    match section_data.read_from:
        case ReadFromPlural():
            return _read_blog(
                section=section_data,
                breadcrumbs=breadcrumbs,
                website_info=website_info,
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
