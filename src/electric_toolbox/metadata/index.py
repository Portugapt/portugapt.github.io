"""Index data build."""

from expression import Error, Ok, Result
from pydantic import ValidationError

from electric_toolbox.markup.read_markdown import markdown_to_html_no_frontmatter
from electric_toolbox.metadata.types.metadata import Index
from electric_toolbox.parse_configs import SiteConfigs


def create_meta_index(configs: SiteConfigs) -> Result[Index, Exception]:
    """Creates a Head instance from SiteConfigs.

    Args:
        configs: The website configuration.

    Returns:
        A Head instance.
    """
    try:
        with open(configs.contents.index) as indx:
            _content = markdown_to_html_no_frontmatter(indx.read())
        return Ok(Index(contents=_content))
    except ValidationError as e:
        return Error(Exception('Error creating head metadata', e))
