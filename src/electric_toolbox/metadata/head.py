"""Create head data."""

from expression import Error, Ok, Result
from pydantic import ValidationError

from electric_toolbox.metadata.types.metadata import Head
from electric_toolbox.parse_configs import SiteConfigs


def create_meta_head(configs: SiteConfigs) -> Result[Head, Exception]:
    """Creates a Head instance from SiteConfigs.

    Args:
        configs: The website configuration.

    Returns:
        A Head instance.
    """
    try:
        return Ok(Head(title=configs.head.title))
    except ValidationError as e:
        return Error(Exception('Error creating head metadata', e))
