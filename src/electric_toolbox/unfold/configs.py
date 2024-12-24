"""Read configurations."""

from typing import Any, Dict, Generator

from expression import Error, Ok, Result, effect
from pydantic import ValidationError

from electric_toolbox.unfold.types.configs import ConfigContents, ConfigHead, ConfigSettings, SiteConfigs


def _parse_config_settings(data: Dict[str, Any]) -> Result[ConfigSettings, Exception]:
    """Parses config settings.

    Args:
        data: The settings data.

    Returns:
        Result[ConfigSettings, Exception]: Ok(ConfigSettings) if successful,
            Error(Exception) if validation fails.
    """
    try:
        return Ok(ConfigSettings(**data))
    except ValidationError as e:
        return Error(Exception('Invalid config settings', e))


def _parse_config_head(data: Dict[str, Any]) -> Result[ConfigHead, Exception]:
    """Parses config head.

    Args:
        data: The head data.

    Returns:
        Result[ConfigHead, Exception]: Ok(ConfigHead) if successful,
            Error(Exception) if validation fails.
    """
    try:
        return Ok(ConfigHead(**data))
    except ValidationError as e:
        return Error(Exception('Invalid config head', e))


def _parse_config_contents(data: Dict[str, Any]) -> Result[ConfigContents, Exception]:
    """Parses config contents.

    Args:
        data: The contents data.

    Returns:
        Result[ConfigContents, Exception]: Ok(ConfigContents) if successful,
            Error(Exception) if validation fails.
    """
    try:
        return Ok(ConfigContents(**data))
    except ValidationError as e:
        return Error(Exception('Invalid config contents', e))


@effect.result[SiteConfigs, Exception]()
def parse_website_config(configs: Dict[str, Any]) -> Generator[Any, Any, SiteConfigs]:
    """Parse website configuration data.

    Args:
        configs: The website configuration data.

    Returns:
        Result[SiteConfigs, Exception]: Ok(SiteConfigs) if successful,
            Error(Exception) if parsing or validation fails.
    """
    return SiteConfigs(
        settings=(yield from _parse_config_settings(configs.get('settings', {}))),
        head=(yield from _parse_config_head(configs.get('head', {}))),
        contents=(yield from _parse_config_contents(configs.get('contents', {}))),
    )
