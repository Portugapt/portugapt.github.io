"""Read and create all website data."""

from pathlib import Path
from typing import Any, Dict, Generator

from expression import effect

from electric_toolbox.common.files_management import list_folder_files
from electric_toolbox.unfold.configs import parse_website_config
from electric_toolbox.unfold.posts import read_all_posts
from electric_toolbox.unfold.types.website import WebsiteMatadata


@effect.result[WebsiteMatadata, Exception]()
def website_unfolded(
    configs_loaded: Dict[str, Any],
) -> Generator[Any, Any, WebsiteMatadata]:
    """Read and create all website data."""
    configs = yield from parse_website_config(configs=configs_loaded)

    return WebsiteMatadata(
        title=configs.head.title,
        posts=(yield from read_all_posts(files=list_folder_files(path=Path(configs.contents.posts)))),
    )
