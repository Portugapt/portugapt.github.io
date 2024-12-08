"""Read configurations."""

from typing import Any, Dict

from expression import Result
from pydantic import BaseModel, ConfigDict, ValidationError


class ConfigSettings(BaseModel):
    """Website settings."""

    model_config = ConfigDict(frozen=True, strict=True)
    include_drafts: bool = False


class ConfigHead(BaseModel):
    """Head data."""

    model_config = ConfigDict(frozen=True, strict=True)
    title: str


class ConfigContents(BaseModel):
    """Website contents data."""

    model_config = ConfigDict(frozen=True)
    index: str
    posts: str


class SiteConfigs(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)
    settings: ConfigSettings
    head: ConfigHead
    contents: ConfigContents


def _create_site_configs(
    settings: ConfigSettings,
    head: ConfigHead,
    contents: ConfigContents,
) -> Result[SiteConfigs, Exception]:
    """Create a `SiteConfigs` instance.

    Args:
        settings: The website settings.
        head: The website head data.
        contents: The website contents data.

    Returns:
        An `Ok` result with the `SiteConfigs` object if successful, or an `Error` result if validation fails.
    """
    try:
        return Result.Ok(
            SiteConfigs(
                settings=settings,
                head=head,
                contents=contents,
            )
        )
    except ValidationError as e:
        return Result.Error(Exception('Error happened converting configs.', e))


def parse_website_config(configs: Dict[str, Any]) -> Result[SiteConfigs, Exception]:
    """Parse website configuration data.

    Args:
        configs: The website configuration data.

    Returns:
        An `Ok` result with the `SiteConfigs` object if successful, or an `Error` result if parsing or validation fails.
    """
    match configs:
        case {
            'settings': dict(var_settings),
            'head': dict(var_head),
            'contents': dict(var_contents),
        }:
            return _create_site_configs(
                ConfigSettings(**var_settings), ConfigHead(**var_head), ConfigContents(**var_contents)
            )
        case _:
            return Result.Error(Exception('Could not read settings.'))
