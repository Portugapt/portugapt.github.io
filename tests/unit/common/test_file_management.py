"""Test file management."""

from pathlib import Path

from deepdiff.diff import DeepDiff
from expression.collections import Map

from electric_toolbox.common.types.file import FileData


def test_list_folder_files(snap_posts_01: Map[str, FileData]) -> None:
    """Test list_folder_files."""
    assert {} == DeepDiff(
        snap_posts_01,
        Map.of_list(
            lst=[
                (
                    'A very: Compilcated name - Hi.md',
                    FileData(
                        path=Path('tests/data/snap_posts_01/A very: Compilcated name - Hi.md'),
                        file_name='A very: Compilcated name - Hi.md',
                        contents='# Complicated Name\n\nLorem ipsum 02\n',
                    ),
                ),
                (
                    'test1.md',
                    FileData(
                        path=Path('tests/data/snap_posts_01/test1.md'),
                        file_name='test1.md',
                        contents="""# Hello World

Lorem ipsum 01
""",
                    ),
                ),
            ],
        ),
        ignore_order=True,
        exclude_paths=[
            "root['A very: Compilcated name - Hi.md'].path",
            "root['test1.md'].path",
        ],  # Exclude path from comparison
    )
