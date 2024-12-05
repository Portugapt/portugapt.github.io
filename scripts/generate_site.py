import electric_toolbox
from jinja2 import Environment, PackageLoader
from pathlib import Path

WEBSITE_DIRECTORY: Path = Path("website")
electric_toolbox.clean_and_recreate(WEBSITE_DIRECTORY)


jinja_env = Environment( loader= PackageLoader('electric_toolbox', 'templates'))

electric_toolbox.build_index(path=WEBSITE_DIRECTORY, j2_env=jinja_env)