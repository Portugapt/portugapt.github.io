"""Entrypoint to website generation."""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment


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
    pass
