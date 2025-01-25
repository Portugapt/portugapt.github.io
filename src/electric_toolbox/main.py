"""Entrypoint to website generation."""

from pathlib import Path
from typing import Any, Dict

from expression import Result
from jinja2 import Environment

from electric_toolbox.configs import parse_website_config
from electric_toolbox.parsing import create_website_view_model, parse_website

from .generate import generate


def main(
    base_path: Path,
    j2_env: Environment,
    configs: Dict[str, Any],
) -> None:
    """Entrypoint to generate website.

    Args:
        path (Path): Root path/folder of the static website.
        j2_env (Environment): Jinja2 Templates envornment.
        configs (Dict[str, Any]): Website configurations.
    """
    match parse_website_config(configs):
        case Result(tag='ok', ok=configs_loaded):
            match parse_website(configs=configs_loaded):
                case Result(tag='ok', ok=website):
                    generate(
                        base_path=base_path,
                        env=j2_env,
                        website=create_website_view_model(website),
                    )
                case Result(error=website_error):
                    raise website_error
        case Result(error=configs_error):
            raise configs_error
