"""Common funnctions for the views."""

from pathlib import Path

from electric_toolbox.unfold.types.website import WebsiteMatadata


def url_inference(metadata: WebsiteMatadata, file_as_path: Path) -> str:
    """Infers the URL for a given file path.

    Args:
        metadata: The website metadata.
        file_as_path: The file path.

    Returns:
        str: The inferred URL.
    """
    return 'https://' + metadata.configs.human_number + '/' + str(file_as_path.relative_to('website'))
