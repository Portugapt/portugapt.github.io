"""Tests for page_functions."""

from pathlib import Path

import frontmatter  # type: ignore
import pytest
from expression import Ok, Some
from expression.collections import Block, Map
from pydantic import HttpUrl

from electric_toolbox.common.types.file import FileData
from electric_toolbox.new.parsing.components.opengraph.models import OpenGraph, ViewModelOpenGraph
from electric_toolbox.new.parsing.components.opengraph.page_functions import (
    page_from_md_front_matter,
    page_og_to_view_model,
)


@pytest.fixture
def sample_file_data_1(sample_01_list_folder_files: Map[str, FileData]) -> FileData:
    """Sample file data."""
    return sample_01_list_folder_files['test1.md']


@pytest.fixture
def sample_file_data_2() -> FileData:
    """Sample file data."""
    return FileData(
        path=Path('tests/data/snap_posts_01/A very- Complicated name - Hi.md'),
        file_name='A very- Complicated name - Hi.md',
        contents="""---
title: "Complicated Name"
image: "none"
publication_time: 2024-01-01 15:00:00
section: "example_section"
authors:
  - first_name: "João"
    last_name: "Monteiro"
    username: "Portugapt"
    gender: "male"
    email: "monteiro.joao.ps@gmail.com"
language: "en"
stage: "draft"
tags:
  - "example"
  - "example2"
content_type: "blog"
---
# Complicated Name

Lorem ipsum 02
""",
    )


@pytest.fixture
def sample_file_data_invalid_frontmatter() -> FileData:
    """Sample file data with invalid front matter."""
    return FileData(
        path=Path('tests/data/invalid_frontmatter.md'),
        file_name='invalid_frontmatter.md',
        contents="""---
invalid_field: "This should cause an error"
---
# Invalid Frontmatter
""",
    )


def test_from_markdown_frontmatter_valid(
    sample_file_data_1: FileData,
) -> None:
    """Test from_markdown_frontmatter with valid front matter."""
    post = frontmatter.loads(sample_file_data_1.contents)
    url = 'https://example.com/path/to/post'

    expected = Ok(
        OpenGraph(
            title='A Sample test post',
            ogtype='article',
            image='https://example.com/image.jpg',
            description=Some('This is a sample description'),
            locale='en',
            url=HttpUrl(url),
        )
    )

    result = page_from_md_front_matter(
        data=post,
        url=url,
    )

    assert result == expected


def test_from_markdown_frontmatter_invalid(
    sample_file_data_1: FileData,
) -> None:
    """Test from_markdown_frontmatter with invalid front matter."""
    post = frontmatter.loads(sample_file_data_1.contents)
    post.metadata['title'] = None  # Make the title invalid
    url = 'https://example.com/path/to/post'

    result = page_from_md_front_matter(
        data=post,
        url=url,
    )

    assert result.is_error()


def test_to_view_model_valid_page() -> None:
    """Test to_view_model with a valid OpenGraph object."""
    og = OpenGraph(
        title='Test Title',
        ogtype='website',
        image='https://example.com/image.jpg',
        url=HttpUrl('https://example.com'),
        locale='en_US',
        description=Some('Test description'),
        site_name=Some('Test Site'),
        audio=Some('https://example.com/audio.mp3'),
        video=Some('https://example.com/video.mp4'),
        determiner=Some('the'),
        locale_alternate=Some(Block.of_seq(['es_ES', 'fr_FR'])),
    )

    expected_parts = Block.of_seq(
        [
            '<meta property="og:title" content="Test Title">',
            '<meta property="og:type" content="website">',
            '<meta property="og:image" content="https://example.com/image.jpg">',
            '<meta property="og:url" content="https://example.com/">',
            '<meta property="og:locale" content="en_US">',
            '<meta property="og:audio" content="https://example.com/audio.mp3">',
            '<meta property="og:description" content="Test description">',
            '<meta property="og:determiner" content="the">',
            '<meta property="og:site_name" content="Test Site">',
            '<meta property="og:video" content="https://example.com/video.mp4">',
            '<meta property="og:locale:alternate" content="es_ES">',
            '<meta property="og:locale:alternate" content="fr_FR">',
        ]
    )

    expected = ViewModelOpenGraph(parts=expected_parts)
    actual = page_og_to_view_model(og)
    assert actual == expected


def test_to_view_model_minimum_page() -> None:
    """Test to_view_model with a valid OpenGraph object with minimum data."""
    og = OpenGraph(
        title='Test Title',
        ogtype='website',
        image='https://example.com/image.jpg',
        url=HttpUrl('https://example.com'),
        locale='en_US',
    )

    expected_parts = Block.of_seq(
        [
            '<meta property="og:title" content="Test Title">',
            '<meta property="og:type" content="website">',
            '<meta property="og:image" content="https://example.com/image.jpg">',
            '<meta property="og:url" content="https://example.com/">',
            '<meta property="og:locale" content="en_US">',
        ]
    )

    expected = ViewModelOpenGraph(parts=expected_parts)
    actual = page_og_to_view_model(og)
    assert actual == expected
