"""Read markdown file."""

import re

import markdown


def remove_frontmatter(markdown_text: str) -> str:
    """Removes frontmatter from markdown.

    Args:
        markdown_text: The markdown text to render.

    Returns:
        The rendered HTML string.
    """
    # Remove frontmatter using regular expression
    return re.sub(r'^---(.*?)---\n', '', markdown_text, flags=re.DOTALL)


def markdown_to_html_no_frontmatter(contents: str) -> str:
    """Read contents. WIP."""
    return markdown.markdown(
        remove_frontmatter(contents),
        extensions=[
            'attr_list',
        ],
    )


def read_frontmatter(contents: str) -> None:
    """WIP. Read frontmatter."""
    pass
