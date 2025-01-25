"""Parse website data."""

from typing import Any, Generator

from expression import Nothing, effect

from electric_toolbox.configs import SiteConfigs
from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing.common import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs

from .models import Website
from .sections import read_blog, read_homepage


@effect.result[Website, Exception]()
def main(
    configs: SiteConfigs,
) -> Generator[Any, Any, Website]:
    """Entrypoint to generate website data.

    Args:
        configs (Dict[str, Any]): Website configurations.
    """
    initial_breadcrumbs = Breadcrumbs(
        path='/index',
        title='Home',
        targets=TargetFiles(
            complete=Template(
                destination='index',
                template=ExistingTemplates.INDEX,
                extension='html',
            ),
            hx=Template(
                destination='index_hx',
                template=ExistingTemplates.INDEX_HX,
                extension='html',
            ),
        ),
        previous_crumb=Nothing,
    )

    blog = yield from read_blog(
        sections=configs.sections,
        website_info=configs.website,
        base_url=configs.base_url,
    )

    homepage = yield from read_homepage(
        sections=configs.sections,
        website_info=configs.website,
        home_crumb=initial_breadcrumbs,
        base_url=configs.base_url,
    )
    return Website(
        homepage=homepage,
        blog=blog,
    )
