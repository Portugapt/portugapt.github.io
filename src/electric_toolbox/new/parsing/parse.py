"""Parse website data."""

from typing import Any, Generator

from expression import Nothing, Some, effect

from electric_toolbox.new.configs import SiteConfigs
from electric_toolbox.new.parsing.components.breadcrumbs import Breadcrumbs

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
    initial_breadcrumbs = Some(
        Breadcrumbs(
            path='/',
            title=configs.website.title,
            previous_crumb=Nothing,
        )
    )
    blog = yield from read_blog(
        sections=configs.sections,
        previous_crumb=initial_breadcrumbs,
        base_url=configs.base_url,
    )

    homepage = yield from read_homepage(
        sections=configs.sections,
        website_info=configs.website,
        previous_crumb=initial_breadcrumbs,
        base_url=configs.base_url,
    )
    return Website(
        homepage=homepage,
        blog=blog,
    )
