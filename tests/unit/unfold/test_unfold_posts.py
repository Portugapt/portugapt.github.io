"""Tests for read_markdown."""

from datetime import datetime
from pathlib import Path

import pytest
from expression import Nothing, Result, Some
from expression.collections import Block, Map

from electric_toolbox.common.types.file import FileData
from electric_toolbox.unfold.posts import read_all_posts, read_post
from electric_toolbox.unfold.types.common import Author, OpenGraph
from electric_toolbox.unfold.types.post import FrontMatter, Post, PostOpenGraph


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
tags: ["tag_hello", "tag_world"]
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


def test_read_post_valid(sample_file_data_1: FileData) -> None:
    """Test read_post with a valid post."""
    actual: Result[Post, Exception] = read_post(sample_file_data_1)
    assert actual.is_ok()
    assert actual.ok == Post(
        slug='test1',
        file_path='tests/data/snap_posts_01/test1.md',
        reading_time='1 min',
        contents='<h1>Hello World</h1>\n<p>Lorem ipsum 01</p>',
        head_extras=Nothing,
        front_matter=FrontMatter(
            opengraph=OpenGraph(
                title='A Sample test post',
                ogtype='article',
                image='https://example.com/image.jpg',
                description=Some('This is a sample description'),
                locale='en',
            ),
            post_opengraph=PostOpenGraph(
                publication_time=datetime(2024, 1, 1, 15, 0, 0).isoformat(),
                modified_time=datetime(2024, 1, 1, 15, 0, 0).isoformat(),
                expiration_time=datetime(2026, 1, 1, 15, 0, 0).isoformat(),
                authors=Block.of_seq(
                    [
                        Author(
                            first_name='João',
                            last_name='Monteiro',
                            username='Portugapt',
                            gender='male',
                            email=Some('monteiro (dot) joao (dot) ps (at) gmail (dot) com'),
                            url=Nothing,
                        )
                    ]
                ),
                section='Example_fm1',
                tags=Block.of_seq(['tag1', 'tag2']),
            ),
            stage='draft',
        ),
    )


def test_read_post_invalid_frontmatter(
    sample_file_data_invalid_frontmatter: FileData,
) -> None:
    """Test read_post with a post that has invalid front matter."""
    actual = read_post(sample_file_data_invalid_frontmatter)
    assert actual.is_error()
    assert isinstance(actual.error, Exception)


def test_read_post_missing_title(sample_file_data_1: FileData) -> None:
    """Test read_post with a post that's missing a title."""
    # Modify the sample data to be missing a title
    sample_file_data_1.contents = """---
authors:
  - first_name: "João"
    last_name: "Monteiro"
    username: "Portugapt"
    gender: "male"
    email: "monteiro (dot) joao (dot) ps (at) gmail (dot) com"
stage: "draft"
publish_date: 2024-01-01
tags: ["tag1", "tag2"]
content_type: "blog"
---
# No Title

Lorem ipsum
"""
    actual = read_post(sample_file_data_1)
    assert actual.is_error()


def test_read_all_posts_valid(sample_file_data_1: FileData, sample_file_data_2: FileData) -> None:
    """Test read_all_posts with valid posts."""
    files = Map.of_list(
        [
            ('test1.md', sample_file_data_1),
            ('A very: Compilcated name - Hi.md', sample_file_data_2),
        ]
    )
    actual = read_all_posts(files)
    print(actual)
    assert actual.is_ok()

    posts = actual.ok  # Access the Ok value (the Map)

    assert len(posts) == 2
    assert 'test1' in [p.slug for p in posts.take_last(2)]
    assert 'a-very-complicated-name-hi' in [p.slug for p in posts.take_last(2)]


def test_read_all_posts_invalid(sample_file_data_1: FileData, sample_file_data_invalid_frontmatter: FileData) -> None:
    """Test read_all_posts with one valid and one invalid post."""
    files = Map.of_list(
        [
            ('test1.md', sample_file_data_1),
            ('invalid_frontmatter.md', sample_file_data_invalid_frontmatter),
        ]
    )
    actual = read_all_posts(files)
    assert actual.is_error()


def test_read_post_empty_frontmatter(tmp_path: Path) -> None:
    """Test read_post with a post that has empty frontmatter."""
    # Create a temporary file with empty frontmatter
    file_path = tmp_path / 'empty_frontmatter.md'
    file_path.write_text('---\n---\n# Empty Frontmatter')

    file_data = FileData(path=file_path, file_name='empty_frontmatter.md', contents='')

    actual = read_post(file_data)
    assert actual.is_error()
    # assert actual.is_ok()
    # post = actual.ok

    # # Check that default values are used when frontmatter is empty
    # assert post.front_matter.author == default_author()
    # assert post.front_matter.title == ''  # Or some other default behavior you define
    # assert post.front_matter.language == 'en'
    # assert post.front_matter.stage == 'draft'
    # assert post.front_matter.publish_date == Nothing
    # assert post.front_matter.tags.is_empty()
    # assert post.front_matter.content_type == 'blog'


def test_read_post_no_frontmatter(tmp_path: Path) -> None:
    """Test read_post with a post that has no frontmatter at all."""
    # Create a temporary file with no frontmatter
    file_path = tmp_path / 'no_frontmatter.md'
    file_path.write_text('# No Frontmatter\n\nSome content here.')

    file_data = FileData(path=file_path, file_name='no_frontmatter.md', contents='')

    actual = read_post(file_data)
    assert actual.is_error()
    assert 'Title not found' in str(actual.error)
