"""Parsing of the posts folder."""

from pathlib import Path
from typing import Dict

from electric_toolbox.common.to_file import string_to_file
from electric_toolbox.metadata.types.metadata import WebsiteMatadata


def metadata_to_post(
    metadata: WebsiteMatadata,
) -> Dict[str, str]:
    """Converts website metadata to index page data.

    Args:
        metadata: The website metadata.

    Returns:
        The index page data.
    """
    print(metadata.posts)
    return {k: v.contents for k, v in metadata.posts.items()}


def generate_posts(
    metadata: WebsiteMatadata,
    root_path: Path,
    folder: str = 'posts',
    to_file: bool = True,
) -> Dict[str, str]:
    """Generates HTML files for blog posts.

    Processes website metadata to create individual HTML files for each blog post.
    Optionally writes the generated HTML to files in a specified folder.

    Args:
        metadata: The website metadata containing post information.
        root_path: The root directory where the posts folder will be created/accessed.
        folder: The name of the folder to store the generated post HTML files. Defaults to 'posts'.
        to_file: Whether to write the generated HTML to files. Defaults to True.

    Returns:
        A dictionary mapping post slugs to their corresponding rendered HTML content.
    """
    if not (root_path / folder).exists():
        (root_path / folder).mkdir()
    posts = metadata_to_post(metadata=metadata)
    for slug, post in posts.items():
        string_to_file(
            path=(root_path / folder),
            file_name=f'{slug}.html',
            contents=post,
        )

    return posts
