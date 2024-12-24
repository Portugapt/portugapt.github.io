"""Post data build."""

from pathlib import Path
from typing import Dict

from expression import Error, Ok, Result
from pydantic import ValidationError

from electric_toolbox.common.files_management import list_folder_files
from electric_toolbox.markup.read_markdown import markdown_to_html_no_frontmatter
from electric_toolbox.metadata.types.metadata import Post
from electric_toolbox.parse_configs import SiteConfigs


def to_slug(file: str) -> str:
    """Sluggify."""
    return file.split('.')[0].replace('-', '_')


def create_meta_posts(configs: SiteConfigs) -> Result[Dict[str, Post], Exception]:
    """Creates a Head instance from SiteConfigs.

    Args:
        configs: The website configuration.

    Returns:
        A Head instance.
    """
    try:
        posts = list_folder_files(path=Path(configs.contents.posts), key_transformer=to_slug)

        return Ok(dict(posts.map(lambda _, d: Post(contents=markdown_to_html_no_frontmatter(d.contents)))))

    except ValidationError as e:
        return Error(Exception('Error creating head metadata', e))
