"""Homepage functions."""

from typing import Dict, Literal

from expression import Error, Result
from pydantic import HttpUrl

from electric_toolbox.configs import ReadFromSingular, Section, WebsiteInfo
from electric_toolbox.parsing.common import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs
from electric_toolbox.parsing.components.navigation import create_navigation_menu
from electric_toolbox.parsing.components.opengraph import create_opengraph_typed_website

from .models import HomePage


def read_homepage(
    sections: Dict[str, Section],
    website_info: WebsiteInfo,
    home_crumb: Breadcrumbs,
    base_url: str = '',
    section: Literal['home'] = 'home',
) -> Result[HomePage, Exception]:
    """Create a view model for the home page."""
    section_data = sections[section]

    match section_data.read_from:
        case ReadFromSingular():
            a = section_data.read_from
            return create_opengraph_typed_website(
                title=website_info.title,
                description=website_info.description,
                image=website_info.image,
                locale=website_info.locale,
                url=base_url,
            ).map(
                lambda opengraph: HomePage(
                    title=section_data.title,
                    resource_path=section_data.resource_path,
                    targets=TargetFiles(
                        complete=Template(
                            destination='index.html',
                            template=home_crumb.targets.complete.template,
                            extension=home_crumb.targets.complete.extension,
                        ),
                        hx=Template(
                            destination='index_hx.html',
                            template=home_crumb.targets.hx.template,
                            extension=home_crumb.targets.hx.extension,
                        ),
                    ),
                    contents=a.file.contents,
                    navigation=create_navigation_menu(
                        sections=sections,
                        requester_section=section_data.title,
                        base_url=base_url,
                    ),
                    opengraph=opengraph,
                    base_url=HttpUrl(base_url),
                )
            )

        case _:
            return Error(Exception(f'Unknown read_from type: {section_data.read_from}'))
