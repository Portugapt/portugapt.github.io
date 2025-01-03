"""Entrypoint to website generation."""

from pathlib import Path
from typing import Any, Dict

from expression import Result
from jinja2 import Environment

from electric_toolbox.metadata.website_metadata import website_metadata
from electric_toolbox.unfold.website import website_unfolded
from electric_toolbox.view import index as generate_index
from electric_toolbox.view.new.posts import generate_post_blocks


def main(
    path: Path,
    j2_env: Environment,
    configs: Dict[str, Any],
) -> None:
    """Entrypoint to generate website.

    Args:
        path (Path): Root path/folder of the static website.
        j2_env (Environment): Jinja2 Templates envornment.
        configs (Dict[str, Any]): Website configurations.
    """
    metadata = website_metadata(configs=configs)
    metadata2 = website_unfolded(configs_loaded=configs)
    generate_post_blocks(
        metadata=metadata2.ok,
        j2_env=j2_env,
        root_path=path,
    )
    match metadata:
        case Result(tag='ok', ok=_website):
            generate_index(
                j2_env=j2_env,
                metadata=_website,
                root_path=path,
            )
