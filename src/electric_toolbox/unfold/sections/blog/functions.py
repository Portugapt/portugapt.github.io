"""Functions for parsing blog posts."""

import re
from datetime import datetime, timedelta
from typing import Any, Generator

import frontmatter  # type: ignore
from expression import Error, Ok, Option, Result, effect
from markdown import Markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from pydantic import HttpUrl
from pymdownx.superfences import SuperFencesCodeExtension  # type: ignore
from slugify import slugify

from electric_toolbox.common.types.file import FileData
from electric_toolbox.unfold.components.breadcrumbs import Breadcrumbs, generate_url
from electric_toolbox.unfold.components.opengraph import article_from_md_front_matter, page_from_md_front_matter

from .models import BlogPost

MarkdownMetadata = dict[str, Any]
ONE_HOUR = 60


def _to_slug(file_name: str) -> str:
    """Converts a file name to a URL-friendly slug.

    Args:
        file_name: The input file name.

    Returns:
        Slug: A URL-friendly slug.
    """
    name_without_extension = file_name.split('.')[0]
    return slugify(name_without_extension)


def _estimate_reading_time(text: str, WPM: int = 200) -> str:
    """Estimate the reading time of a text.

    Args:
        text: The text to estimate the reading time of.
        WPM: The words per minute to use.

    Returns:
        The estimated reading time.
    """
    total_words = len(re.findall(r'\w+', text))
    time_minute = total_words // WPM + 1
    if time_minute == 0:
        time_minute = 1
    elif time_minute > ONE_HOUR:
        return str(time_minute // 60) + ' h'
    return str(time_minute) + ' min'


def _parse_title(data: MarkdownMetadata) -> Result[str, Exception]:
    """Parses the title from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[str, Exception]: Ok(str) containing the title if present,
            Error(Exception) if the title is missing.
    """
    title = data.get('title')
    if title is not None:
        return Ok(title)
    return Error(Exception('Title not found'))


def _parse_date(data: MarkdownMetadata, add_time: timedelta = timedelta(days=0)) -> Result[str, Exception]:
    """Parses the publish date from the post's metadata.

    Args:
        data: The metadata dictionary.
        add_time: The time to add to the publish date.

    Returns:
        Result[Option[datetime], Exception]: Ok(Option[datetime]) containing the publish date if present and valid,
            Error(Exception) if the publish date is invalid.
    """
    date_obj = data.get('publication_time')
    match date_obj:
        case datetime():
            return Ok((date_obj + add_time).isoformat())
        case _:
            return Error(Exception('Frontmatter `publication_time` must be an ISO8601 datetime string'))


def _md_to_html(contents: str) -> str:
    """Converts Markdown content to HTML using the `markdown` library.

    Args:
        contents: The Markdown content.

    Returns:
        str: The HTML representation of the Markdown content.
    """
    md = Markdown(
        extensions=[
            'attr_list',
            SuperFencesCodeExtension(css_class='code-block'),
            CodeHiliteExtension(css_class='code-block', linenos='table'),
        ]
    )
    return md.convert(contents)


def _create_breadcrumbs(
    file_name: str,
    title: str,
    previous_crumb: Option[Breadcrumbs],
) -> Breadcrumbs:
    """Creates a breadcrumb trail for the post.

    Args:
        file_name: The name of the post file.
        title: The title of the post.
        previous_crumb: The previous breadcrumb trail.

    Returns:
        Breadcrumbs: The breadcrumb trail for the post.
    """
    return Breadcrumbs(
        path=_to_slug(file_name),
        title=title,
        previous_crumb=previous_crumb,
    )


@effect.result[BlogPost, Exception]()
def read_post(
    file: FileData,
    previous_crumb: Option[Breadcrumbs],
    base_url: str = '',
) -> Generator[Any, Any, BlogPost]:
    """Reads a post from a `FileData` object.

    Parses the front matter and converts the Markdown content to HTML.

    Args:
        file: The `FileData` object containing the post file.
        previous_crumb: The previous breadcrumb trail.
        base_url: The base URL to use for the breadcrumb trail. Defaults to an empty string.

    Returns:
        BlogPost: The parsed post.
    """
    unfolded_post: frontmatter.Post = frontmatter.loads(file.contents)
    title = yield from _parse_title(unfolded_post.metadata)
    breadcrumbs = _create_breadcrumbs(file.file_name, title, previous_crumb)
    url = generate_url(breadcrumbs, base_url=base_url)
    print(url)
    return BlogPost(
        title=title,
        date=(yield from _parse_date(unfolded_post.metadata)),
        contents=_md_to_html(unfolded_post.content),
        base_url=HttpUrl(base_url),
        url=HttpUrl(url),
        reading_time=_estimate_reading_time(unfolded_post.content),
        breadcrumbs=breadcrumbs,
        opengraph=(
            yield from page_from_md_front_matter(
                data=unfolded_post,
                url=url,
            )
        ),
        article_opengraph=(
            yield from article_from_md_front_matter(
                data=unfolded_post,
            )
        ),
    )
