"""Read configurations."""

from typing import Any, Dict, Generator

from expression import Error, Ok, Result, effect
from pydantic import ValidationError

from electric_toolbox.unfold.types.configs import (
    ConfigContents,
    ConfigHead,
    ConfigSettings,
    ReadFrom,
    ReadFromPlural,
    ReadFromSingular,
    Section,
    SiteConfigs,
)


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


def _parse_read_from(data: Dict[str, Any]) -> Result[ReadFrom, Exception]:
    """Parses read_from configuration.

    Args:
        data: The read_from data.

    Returns:
        Result[ReadFrom, Exception]: Ok(ReadFrom) if successful,
            Error(Exception) if validation fails.
    """
    try:
        if data['type'] == 'singular':
            return Ok(ReadFromSingular(**data))
        elif data['type'] == 'plural':
            return Ok(ReadFromPlural(**data))
        else:
            return Error(Exception(f"Invalid read_from type: {data['type']}"))
    except ValidationError as e:
        return Error(Exception('Invalid read_from configuration', e))
    except KeyError as e:
        return Error(Exception('Missing read_from type', e))


@effect.result[Section, Exception]()
def _parse_section(data: Dict[str, Any]) -> Generator[Any, Any, Section]:
    """Parses a single section.

    Args:
        data: The section data.

    Returns:
        Result[Section, Exception]: Ok(Section) if successful,
            Error(Exception) if validation fails.
    """

    def _get_title(data: Dict[str, Any]) -> Result[str, Exception]:
        """Gets the title from the data."""
        try:
            return Ok(data['title'])
        except KeyError as e:
            return Error(Exception(f'Missing title field in section configuration: {e}', e))

    def _get_description(data: Dict[str, Any]) -> Result[str, Exception]:
        """Gets the description from the data."""
        try:
            return Ok(data['description'])
        except KeyError as e:
            return Error(Exception(f'Missing description field in section configuration: {e}', e))

    def _get_url(data: Dict[str, Any]) -> Result[str, Exception]:
        """Gets the url from the data."""
        try:
            return Ok(data['url'])
        except KeyError as e:
            return Error(Exception(f'Missing url field in section configuration: {e}', e))

    return Section(
        title=(yield from _get_title(data)),
        description=(yield from _get_description(data)),
        url=(yield from _get_url(data)),
        read_from=(yield from _parse_read_from(data['read_from'])),
    )


@effect.result[Dict[str, Section], Exception]()
def _parse_config_sections(data: Dict[str, Any]) -> Generator[Any, Any, Dict[str, Section]]:
    """Parses config sections.

    Args:
        data: The sections data.

    Returns:
        Result[ConfigSections, Exception]: Ok(ConfigSections) if successful,
            Error(Exception) if validation fails.
    """
    sections = {}
    for name, section_data in data.items():
        section_result = yield from _parse_section(section_data)
        sections[name] = section_result
    return sections


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
        human_number=configs.get('human_number', ''),
        settings=(yield from _parse_config_settings(configs.get('settings', {}))),
        head=(yield from _parse_config_head(configs.get('head', {}))),
        contents=(yield from _parse_config_contents(configs.get('contents', {}))),
        sections=(yield from _parse_config_sections(configs.get('sections', {}))),
    )
