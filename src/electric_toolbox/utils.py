"""Functions for managing the website folder. Mainly used for recreate."""

from pathlib import Path


def remove_directory_tree(start_directory: Path) -> None:
    """Recursively and permanently removes the specified directory files.

    All of its subdirectories, and every file contained in any of those folders.
    """
    for path in start_directory.iterdir():
        if path.is_file():
            if path.suffix == '.css':
                continue
            else:
                path.unlink()
        else:
            remove_directory_tree(path)
            path.rmdir()


def clean_or_create(directory: Path) -> None:
    """Will Cleanup the directory if exists, and then (re)create it.

    Args:
        directory (Path): The desired directory path.
    """
    if directory.exists():
        remove_directory_tree(start_directory=directory)
    else:
        directory.mkdir()
