"""List folder files fixtures."""

from pathlib import Path

import pytest
from expression.collections import Map

from electric_toolbox.common.files_management import list_folder_files
from electric_toolbox.common.types.file import FileData


@pytest.fixture
def snap_posts_01() -> Map[str, FileData]:
    """List folder files fixture."""
    return list_folder_files(
        path=Path('tests/data/snap_posts_01'),
        name_transformer=lambda name: name,
    )


@pytest.fixture
def sample_01_list_folder_files() -> Map[str, FileData]:
    """Sample test for list_folder_files."""
    return Map.of_list(
        lst=[
            (
                'A very: Compilcated name - Hi.md',
                FileData(
                    path=Path('tests/data/snap_posts_01/A very: Compilcated name - Hi.md'),
                    original_name='A very: Compilcated name - Hi.md',
                    transformed_name='A very: Compilcated name - Hi.md',
                    contents='# Complicated Name\n\nLorem ipsum 02',
                ),
            ),
            (
                'test1.md',
                FileData(
                    path=Path('tests/data/snap_posts_01/test1.md'),
                    original_name='test1.md',
                    transformed_name='test1.md',
                    contents='# Hello World\n\nLorem ipsum 01',
                ),
            ),
        ],
    )
