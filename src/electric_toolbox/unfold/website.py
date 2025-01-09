"""Read and create all website data."""

from typing import Any, Dict, Generator

from expression import effect

from electric_toolbox.unfold.configs import parse_website_config
from electric_toolbox.unfold.types.post import PostsIndex
from electric_toolbox.unfold.types.website import WebsiteMatadata


@effect.result[WebsiteMatadata, Exception]()
def website_unfolded(
    configs_loaded: Dict[str, Any],
) -> Generator[Any, Any, WebsiteMatadata]:
    """Read and create all website data."""
    configs = yield from parse_website_config(configs=configs_loaded)

    return WebsiteMatadata(
        configs=configs,
        title=configs.head.title,
        posts_section=PostsIndex(title=''),
    )
