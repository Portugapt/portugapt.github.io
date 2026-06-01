"""Sample file-data fixtures used across the unit tests."""

from pathlib import Path

import pytest
from expression.collections import Map

from electric_toolbox.configs import FileData


def sample_frontmatter_1() -> str:
    """Sample frontmatter."""
    return """---
title: "A Sample test post"
image: "https://example.com/image.jpg"
publication_time: 2024-01-01 15:00:00
section: 'Example_fm1'
description: "This is a sample description"
authors:
    - first_name: "João"
      last_name: "Monteiro"
      username: "Portugapt"
      gender: "male"
      url: "https://github.com/Portugapt"
      email: "monteiro (dot) joao (dot) ps (at) gmail (dot) com"
tags:
  - tag1
  - tag2
---
"""


def sample_frontmatter_2() -> str:
    """Sample frontmatter."""
    return """---
title: "A Sample test post"
publish_date: 2024-01-01 16:00:00
---
"""


def post_sample_1(front_matter: str) -> FileData:
    """Build a sample FileData for `A very: Compilcated name - Hi.md`."""
    return FileData(
        path=Path('tests/data/snap_posts_01/A very: Compilcated name - Hi.md'),
        file_name='A very: Compilcated name - Hi.md',
        contents=f"""{front_matter}
# Complicated Name\n\nLorem ipsum 02""",
    )


def post_sample_2(front_matter: str) -> FileData:
    """Build a sample FileData for `test1.md`."""
    return FileData(
        path=Path('tests/data/snap_posts_01/test1.md'),
        file_name='test1.md',
        contents=f"""{front_matter}
# Hello World

Lorem ipsum 01""",
    )


@pytest.fixture
def sample_01_list_folder_files() -> Map[str, FileData]:
    """Sample mapping of file name to FileData."""
    return Map.of_list(
        lst=[
            (
                'A very: Compilcated name - Hi.md',
                post_sample_1(front_matter=''),
            ),
            (
                'test1.md',
                post_sample_2(front_matter=sample_frontmatter_1()),
            ),
        ],
    )


@pytest.fixture
def sample_02_list_folder_files() -> Map[str, FileData]:
    """Sample mapping of file name to FileData."""
    return Map.of_list(
        lst=[
            (
                'A very: Compilcated name - Hi.md',
                post_sample_1(front_matter=sample_frontmatter_2()),
            ),
            (
                'test1.md',
                post_sample_2(front_matter=sample_frontmatter_1()),
            ),
        ],
    )
