"""Script to generate website."""

import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, PackageLoader

import electric_toolbox
from electric_toolbox.main import main

WEBSITE_DIRECTORY: Path = Path('website')
electric_toolbox.clean_or_create(WEBSITE_DIRECTORY)


jinja_env = Environment(
    loader=PackageLoader('electric_toolbox', 'templates'),
    autoescape=True,
)


with open(Path('compile.config.json'), 'r') as conf:
    configs: Dict[str, Any] = json.loads(conf.read())

main(
    base_path=WEBSITE_DIRECTORY,
    j2_env=jinja_env,
    configs=configs,
)
