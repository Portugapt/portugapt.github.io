"""Read configurations."""

from pathlib import Path
from typing import Any, Dict, Generator

from expression import Error, Ok, Result, effect
from expression.collections import Block
from expression.extra.result import traverse
from pydantic import ValidationError

from .models import (
    ConfigContents,
    ConfigHead,
    ConfigSettings,
    FileData,
    ReadFrom,
    ReadFromPlural,
    ReadFromSingular,
    Section,
    SiteConfigs,
    WebsiteInfo,
)


def create_file_data(
    file_path: Path,
) -> Result[FileData, Exception]:
    """Subfunction to create a FileData instance."""
    try:
        with open(file_path, 'r') as f:
            contents = f.read()
    except Exception as e:
        return Error(Exception('Invalid file data', e))

    return Ok(
        FileData(
            path=file_path,
            file_name=file_path.name,
            contents=contents,
        )
    )


def list_folder_files(
    path: Path,
) -> Block[Path]:
    """Get the files in a folder, into a map, where the keys are the name transformer function.

    Args:
        path (Path): The path to map out. Not recursive.
        key_transformer (Callable[[str], str], optional): The file name transformer function.
            Defaults to λx.x.

    Returns:
        Map[str, str]: The map of files in the folder.
    """
    return Block.of_seq(xs=[file_path for file_path in path.iterdir() if file_path.is_file()])


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


@effect.result[ReadFromSingular, Exception]()
def _parse_read_from_singular(data: Dict[str, Any]) -> Generator[Any, Any, ReadFromSingular]:
    """Parses read_from singular configuration.

    Args:
        data: The read_from data.

    Returns:
        Result[ReadFromSingular, Exception]: Ok(ReadFromSingular) if successful,
            Error(Exception) if validation fails.
    """
    return ReadFromSingular(
        type=data.get('type', 'singular'),
        path=data.get('path', 'will_error'),
        file=(yield from create_file_data(Path(data.get('path', 'will_error')))),
    )


@effect.result[ReadFromPlural, Exception]()
def _parse_read_from_plural(data: Dict[str, Any]) -> Generator[Any, Any, ReadFromPlural]:
    """Parses read_from plural configuration.

    Args:
        data: The read_from data.

    Returns:
        Result[ReadFromPlural, Exception]: Ok(ReadFromPlural) if successful,
            Error(Exception) if validation fails.
    """
    return ReadFromPlural(
        type=data.get('type', 'plural'),
        path=data.get('path', 'will_error'),
        files=(
            yield from traverse(
                create_file_data,
                list_folder_files(
                    Path(
                        data.get('path', 'will_error'),
                    )
                ),
            )
        ),
    )


def _parse_read_from(data: Dict[str, Any]) -> Result[ReadFrom, Exception]:
    """Parses read_from configuration.

    Args:
        data: The read_from data.

    Returns:
        Result[ReadFrom, Exception]: Ok(ReadFrom) if successful,
            Error(Exception) if validation fails.
    """
    match data['type']:
        case 'singular':
            return _parse_read_from_singular(data)
        case 'plural':
            return _parse_read_from_plural(data)
        case _:
            return Error(Exception(f"Invalid read_from type: {data['type']}"))


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
        resource_path=(yield from _get_url(data)),
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


def _parse_website(data: Dict[str, Any]) -> Result[WebsiteInfo, Exception]:
    """Parses config sections.

    Args:
        data: The sections data.

    Returns:
        Result[ConfigSections, Exception]: Ok(ConfigSections) if successful,
            Error(Exception) if validation fails.
    """
    try:
        return Ok(
            WebsiteInfo(
                title=data['title'],
                description=data['description'],
                image=data['image'],
                locale=data['locale'],
            )
        )
    except Exception as e:
        return Error(Exception(f'Invalid website configuration: {e}', e))


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
        base_url=configs.get('base_url', ''),
        website=(yield from _parse_website(configs.get('website', {}))),
        settings=(yield from _parse_config_settings(configs.get('settings', {}))),
        sections=(yield from _parse_config_sections(configs.get('sections', {}))),
    )
