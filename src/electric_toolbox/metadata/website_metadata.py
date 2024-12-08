"""Generate all the website data into a single object."""

from typing import Any, Dict

from expression import Error, Ok, Result

from electric_toolbox.metadata.head import create_meta_head
from electric_toolbox.metadata.index import create_meta_index
from electric_toolbox.metadata.posts import create_meta_posts
from electric_toolbox.metadata.types.metadata import WebsiteMatadata
from electric_toolbox.parse_configs import SiteConfigs, parse_website_config


def website_metadata(
    configs: Dict[str, Any],
) -> Result[WebsiteMatadata, Exception]:
    """Entrypoint to generate website.

    Args:
        path (Path): Root path/folder of the static website.
        j2_env (Environment): Jinja2 Templates envornment.
        configs (Dict[str, Any]): Website configurations.
    """
    config: Result[SiteConfigs, Exception] = parse_website_config(configs=configs)
    web_metadata = (
        config.bind(create_meta_head),
        config.bind(create_meta_index),
        config.bind(create_meta_posts),
    )
    match web_metadata:
        case Result(tag='ok', ok=head), Result(tag='ok', ok=index), Result(tag='ok', ok=posts):
            return Ok(WebsiteMatadata(head=head, index=index, posts=posts))
        case _:
            return Error(Exception([r.error for r in web_metadata if r.is_error()]))
