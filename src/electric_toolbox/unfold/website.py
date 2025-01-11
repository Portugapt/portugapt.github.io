"""Read and create all website data."""

import os
from pathlib import Path
from typing import Any, Dict, Generator

from expression import Some, effect

from electric_toolbox.common.files_management import list_folder_files
from electric_toolbox.unfold.components.breadcrumbs import Breadcrumbs
from electric_toolbox.unfold.configs import parse_website_config
from electric_toolbox.unfold.posts import read_all_posts
from electric_toolbox.unfold.types.post import PostsIndex
from electric_toolbox.unfold.types.website import WebsiteMatadata


@effect.result[WebsiteMatadata, Exception]()
def website_unfolded(
    configs_loaded: Dict[str, Any],
) -> Generator[Any, Any, WebsiteMatadata]:
    """Read and create all website data."""
    configs = yield from parse_website_config(configs=configs_loaded)
    os.environ['ETBX_WEBSITE_DOMAIN'] = configs.human_number

    home_page = Breadcrumbs(
        path=configs.sections['index'].url,
        title=configs.sections['index'].title,
    )
    zeta = WebsiteMatadata(
        configs=configs,
        title=configs.head.title,
        posts_section=PostsIndex(
            title=configs.sections['posts'].title,
            breadcrumbs=Breadcrumbs(
                path=configs.sections['posts'].url,
                title=configs.sections['posts'].title,
                previous_crumb=Some(home_page),
            ),
            items=(
                yield from read_all_posts(
                    files=list_folder_files(
                        path=Path(configs.sections['posts'].read_from.path),
                    )
                )
            ),
        ),
    )
    with open('hey.json', 'w') as f:
        f.write(zeta.model_dump_json(indent=4))
    return zeta
