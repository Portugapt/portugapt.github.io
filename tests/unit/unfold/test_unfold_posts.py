"""Tests for read_markdown."""

from expression.collections import Map

from electric_toolbox.common.types.file import FileData
from electric_toolbox.unfold.posts import one_to_markdown


def test_unfold_snap_posts_01_to_markdown(sample_01_list_folder_files: Map[str, FileData]) -> None:
    """Test read_markdown."""
    actual = one_to_markdown(sample_01_list_folder_files['test1.md'].contents)

    assert (
        actual
        == """<h1>Hello World</h1>
<p>Lorem ipsum 01</p>"""
    )


def test_unfold_snap_posts_01_frontmatter(sample_01_list_folder_files: Map[str, FileData]) -> None:
    """Test read_markdown."""
    pass
    # actual = one_to_markdown(sample_01_list_folder_files['A very: Compilcated name - Hi.md'].contents)
