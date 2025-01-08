"""Tests for configuration parsing."""

from electric_toolbox.unfold.configs import (
    _parse_config_contents,
    _parse_config_head,
    _parse_config_settings,
    parse_website_config,
)
from electric_toolbox.unfold.types.configs import ConfigContents, ConfigHead, ConfigSettings, SiteConfigs


def test_parse_config_settings_valid() -> None:
    """Test parsing valid config settings."""
    data = {'include_drafts': True}
    result = _parse_config_settings(data)
    assert result.is_ok()
    assert result.ok == ConfigSettings(include_drafts=True)


def test_parse_config_settings_invalid() -> None:
    """Test parsing invalid config settings."""
    data = {'include_drafts': 'not a bool'}
    result = _parse_config_settings(data)
    assert result.is_error()
    assert isinstance(result.error, Exception)


def test_parse_config_head_valid() -> None:
    """Test parsing valid config head."""
    data = {'title': 'My Website'}
    result = _parse_config_head(data)
    assert result.is_ok()
    assert result.ok == ConfigHead(title='My Website')


def test_parse_config_head_invalid() -> None:
    """Test parsing invalid config head."""
    data = {'title': 123}  # Title should be a string
    result = _parse_config_head(data)
    assert result.is_error()
    assert isinstance(result.error, Exception)


def test_parse_config_contents_valid() -> None:
    """Test parsing valid config contents."""
    data = {'index': 'index.md', 'posts': 'posts/'}
    result = _parse_config_contents(data)
    assert result.is_ok()
    assert result.ok == ConfigContents(index='index.md', posts='posts/')


def test_parse_config_contents_invalid() -> None:
    """Test parsing invalid config contents."""
    data = {'index': 123, 'posts': 'posts/'}  # Index should be a string
    result = _parse_config_contents(data)
    assert result.is_error()
    assert isinstance(result.error, Exception)


def test_parse_website_config_valid() -> None:
    """Test parsing valid website config."""
    configs = {
        'human_number': 'localhost',
        'settings': {'include_drafts': False},
        'head': {'title': 'My Website'},
        'contents': {'index': 'index.md', 'posts': 'posts/'},
    }
    result = parse_website_config(configs)
    assert result.is_ok()
    assert result.ok == SiteConfigs(
        human_number='localhost',
        settings=ConfigSettings(include_drafts=False),
        head=ConfigHead(title='My Website'),
        contents=ConfigContents(index='index.md', posts='posts/'),
    )


def test_parse_website_config_invalid_settings() -> None:
    """Test parsing website config with invalid settings."""
    configs = {
        'settings': {'include_drafts': 'yes'},
        'head': {'title': 'My Website'},
        'contents': {'index': 'index.md', 'posts': 'posts/'},
    }
    result = parse_website_config(configs)
    assert result.is_error()
    assert isinstance(result.error, Exception)


def test_parse_website_config_missing_section() -> None:
    """Test parsing website config with a missing section."""
    configs = {
        'head': {'title': 'My Website'},
        'contents': {'index': 'index.md', 'posts': 'posts/'},
    }
    result = parse_website_config(configs)
    assert result.is_error()
    assert isinstance(result.error, Exception)  # Expecting an error due to missing settings
