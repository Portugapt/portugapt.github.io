"""FUnctions for managing the website folder. Mainly used for recreate."""

from pathlib import Path
from typing import Callable

from expression.collections import Map

from electric_toolbox.common.types.file import FileData


def remove_directory_tree(start_directory: Path) -> None:
    """Recursively and permanently removes the specified directory files.

    All of its subdirectories, and every file contained in any of those folders.
    """
    for path in start_directory.iterdir():
        if path.is_file():
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


def _create_file_data(
    file_path: Path,
    name_transformer: Callable[[str], str],
) -> FileData:
    """Subfunction to create a FileData instance."""
    with open(file_path, 'r') as f:
        contents = f.read()
    return FileData(path=file_path, transformed_name=name_transformer(file_path.name), contents=contents)


def list_folder_files(
    path: Path,
    name_transformer: Callable[[str], str] = lambda x: x,
) -> Map[str, FileData]:
    """Get the files in a folder, into a map, where the keys are the name transformer function.

    Args:
        path (Path): The path to map out. Not recursive.
        name_transformer (Callable[[str], str], optional): The file name transformer function.
            Defaults to λx.x.

    Returns:
        Map[str, str]: The map of files in the folder.
    """
    return Map.of_seq(
        sequence=[
            (
                name_transformer(file_path.name),
                _create_file_data(
                    file_path,
                    name_transformer=name_transformer,
                ),
            )
            for file_path in path.iterdir()
            if file_path.is_file()
        ]
    )
