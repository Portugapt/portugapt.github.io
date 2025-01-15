"""Tests for configurations functions."""

import tempfile
from pathlib import Path
from typing import Any, Dict

from expression.collections import Block

from electric_toolbox.new.configs import (
    ConfigSettings,
    FileData,
    ReadFromPlural,
    ReadFromSingular,
    Section,
    SiteConfigs,
    parse_website_config,
)


def test_parse_website_config_valid() -> None:
    """Test parse_website_config with valid configuration data."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create dummy files in the temporary directory
        file1 = Path(tmpdirname) / 'file1.txt'
        file1.write_text('Content of file 1')
        file2 = Path(tmpdirname) / 'file2.md'
        file2.write_text('# Markdown Content')

        config_data = {
            'settings': {
                'include_drafts': True,
            },
            'base_url': 'https://example.com',
            'website_name': 'My Website',
            'sections': {
                'blog': {
                    'title': 'Blog',
                    'description': 'My blog posts',
                    'url': '/blog',
                    'read_from': {'type': 'plural', 'path': tmpdirname},
                },
            },
        }

        expected_config = SiteConfigs(
            settings=ConfigSettings(include_drafts=True),
            base_url='https://example.com',
            website_name='My Website',
            sections={
                'blog': Section(
                    title='Blog',
                    description='My blog posts',
                    url='/blog',
                    read_from=ReadFromPlural(
                        type='plural',
                        path=tmpdirname,
                        files=Block.of_seq(
                            xs=[
                                FileData(
                                    file_name='file1.txt',
                                    path=file1,
                                    contents='Content of file 1',
                                ),
                                FileData(
                                    file_name='file2.md',
                                    path=file2,
                                    contents='# Markdown Content',
                                ),
                            ]
                        ),
                    ),
                )
            },
        )

        result = parse_website_config(config_data)
        assert result.is_ok()

        # Verify that result.ok.sections['blog'].read_from.files contains the expected FileData objects
        match result.ok.sections['blog'].read_from:
            case ReadFromPlural(type='plural', path=_, files=files) as read_from_files:
                assert len(files) == 2
                # Check the details of each file
                file_data_1 = read_from_files.files[0]
                assert file_data_1.file_name == 'file1.txt'
                assert file_data_1.path == file1
                assert file_data_1.contents == 'Content of file 1'

                file_data_2 = read_from_files.files[1]
                assert file_data_2.file_name == 'file2.md'
                assert file_data_2.path == file2
                assert file_data_2.contents == '# Markdown Content'
            case _:
                assert False

        # Remove the files attribute before comparison
        assert result.ok == expected_config


def test_parse_website_config_missing_required_fields() -> None:
    """Test parse_website_config with missing required fields in the configuration."""
    config_data: Dict[str, Any] = {}  # Empty config data
    result = parse_website_config(config_data)
    assert result.is_error()


def test_parse_website_config_invalid_read_from_type() -> None:
    """Test parse_website_config with an invalid read_from type."""
    config_data = {
        'settings': {'include_drafts': True},
        'base_url': 'https://example.com',
        'website_name': 'My Website',
        'sections': {
            'blog': {
                'title': 'Blog',
                'description': 'My blog posts',
                'url': '/blog',
                'read_from': {
                    'type': 'invalid',
                    'path': 'path/to/blog/posts',
                },  # Invalid type
            }
        },
    }

    result = parse_website_config(config_data)
    assert result.is_error()


def test_parse_website_config_singular() -> None:
    """Test parse_website_config with a singular read_from."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a temporary file
        file1 = Path(tmpdirname) / 'file1.txt'
        file1.write_text('Content of singular file')

        config_data = {
            'settings': {'include_drafts': False},
            'base_url': 'https://example.com',
            'website_name': 'My Website',
            'sections': {
                'about': {
                    'title': 'About',
                    'description': 'About page',
                    'url': '/about',
                    'read_from': {'type': 'singular', 'path': str(file1)},
                }
            },
        }

        expected_config = SiteConfigs(
            settings=ConfigSettings(include_drafts=False),
            base_url='https://example.com',
            website_name='My Website',
            sections={
                'about': Section(
                    title='About',
                    description='About page',
                    url='/about',
                    read_from=ReadFromSingular(
                        type='singular',
                        path=str(file1),
                        file=FileData(
                            file_name=Path(file1).name,
                            path=Path(file1),
                            contents='Content of singular file',
                        ),
                    ),
                )
            },
        )

        result = parse_website_config(config_data)

        assert result.is_ok()
        assert result.ok == expected_config
