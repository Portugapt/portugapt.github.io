"""Utilies to move an object to a file."""

from pathlib import Path
from typing import TypedDict


class WrittenFile(TypedDict):
    """TypedDict representing a written file."""

    path: Path
    contents: str


def string_to_file(
    path: Path,
    file_name: str,
    contents: str,
) -> WrittenFile:
    """Create a file with the contents string.

    Args:
        path (str): The path to the file.
        file_name (str): The file name (including extension)
        contents (str): The contents to dump into the file.
    """
    with open(path / file_name, 'w') as f:
        f.write(contents)

    return WrittenFile(path=path / file_name, contents=contents)


def create_dir_if_not_exists(path: Path) -> Path:
    """Create a directory if it doesn't exist."""
    if not path.exists():
        path.mkdir(parents=True)

    return path
