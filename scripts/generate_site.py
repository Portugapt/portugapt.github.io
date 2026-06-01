"""Script to generate website."""

import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, PackageLoader

import electric_toolbox
from electric_toolbox.icons import load_icons
from electric_toolbox.main import main

WEBSITE_DIRECTORY: Path = Path('website')
electric_toolbox.clean_or_create(WEBSITE_DIRECTORY)


with open(Path('compile.config.toml'), 'rb') as conf:
    configs: Dict[str, Any] = tomllib.load(conf)

_website: Dict[str, Any] = configs.get('website', {})

jinja_env = Environment(
    loader=PackageLoader('electric_toolbox', 'templates'),
    autoescape=True,
)
jinja_env.globals['icons'] = load_icons(Path('resources/icons'))
jinja_env.globals['site_name'] = _website.get('name') or _website.get('title', '')
jinja_env.globals['build_year'] = datetime.now(tz=timezone.utc).year

main(
    base_path=WEBSITE_DIRECTORY,
    j2_env=jinja_env,
    configs=configs,
)
