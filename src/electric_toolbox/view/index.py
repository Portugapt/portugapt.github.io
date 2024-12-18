"""Build index for the webpage."""

from pathlib import Path
from typing import TypedDict

from jinja2 import Environment

from electric_toolbox.common.to_file import string_to_file
from electric_toolbox.metadata.types.metadata import WebsiteMatadata


class Head(TypedDict):
    """TypedDict representing the head data."""

    title: str


class IndexData(TypedDict):
    """TypedDict representing the index page data."""

    head: Head
    content: str
    footer: str


def metadata_to_page(
    metadata: WebsiteMatadata,
) -> IndexData:
    """Converts website metadata to index page data.

    Args:
        metadata: The website metadata.

    Returns:
        The index page data.
    """
    print(metadata.index.contents)
    return {
        'head': {'title': metadata.head.title},
        'content': metadata.index.contents,
        'footer': 'nothing',
    }


def build(
    j2_env: Environment,
    metadata: WebsiteMatadata,
    root_path: Path,
    to_file: bool = True,
) -> str:
    """Builds the index.html page.

    Renders the index.html page using the provided Jinja2 environment and website metadata.
    Optionally writes the rendered HTML to a file.

    Args:
        j2_env: The Jinja2 environment.
        metadata: The website metadata.
        root_path: The root path where the index.html file will be saved.
        to_file: Whether to write the rendered HTML to a file. Defaults to True.

    Returns:
        The rendered HTML content as a string.
    """
    nav = j2_env.get_template('_base.html')
    contents = nav.render(metadata_to_page(metadata=metadata))
    string_to_file(
        path=root_path,
        file_name='index.html',
        contents=contents,
    )
    return contents
