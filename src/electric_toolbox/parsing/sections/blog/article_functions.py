"""Functions for parsing blog posts."""

import re
from datetime import datetime, timedelta
from typing import Any, Generator

import frontmatter  # type: ignore
from expression import Error, Nothing, Ok, Option, Result, Some, effect
from markdown import Markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from pydantic import HttpUrl
from pymdownx.superfences import SuperFencesCodeExtension  # type: ignore
from slugify import slugify

from electric_toolbox.configs import FileData
from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.exceptions import ParsingError
from electric_toolbox.parsing.common import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs, get_hx_url, get_push_url
from electric_toolbox.parsing.components.opengraph import create_opengraph_article, create_opengraph_typed_article

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


def _parse_title(data: MarkdownMetadata) -> Result[str, ParsingError]:
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
    return Error(
        ParsingError(
            message='Title is missing',
            cause=ValueError(),
            context={
                'function': 'electric_toolbox.parsing.sections.blog.article_functions._parse_title',
            },
        )
    )


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


def _parse_thumbnail(data: MarkdownMetadata) -> Result[Option[str], Exception]:
    """Parses the thumbnail from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Option[str]: The thumbnail URL if present, None otherwise.
    """
    match data.get('thumbnail', Nothing):
        case str(thumbnail):
            return Ok(Some(thumbnail))
        case Option(tag='none'):
            return Ok(Nothing)
        case _:
            return Error(Exception('Frontmatter `thumbnail` must be a string or "none"'))


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
    targets: TargetFiles,
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
        targets=targets,
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
    targets = TargetFiles(
        complete=Template(
            destination=_to_slug(file.file_name),
            template=ExistingTemplates.BLOG_ARTICLE,
            extension='html',
        ),
        hx=Template(
            destination=_to_slug(file.file_name),
            template=ExistingTemplates.BLOG_ARTICLE_HX,
            extension='html',
        ),
    )
    md_file_decomposed: frontmatter.Post = frontmatter.loads(file.contents)
    title = yield from _parse_title(md_file_decomposed.metadata)
    breadcrumbs = _create_breadcrumbs(
        file_name=file.file_name,
        title=title,
        targets=targets,
        previous_crumb=previous_crumb,
    )
    url = get_push_url(breadcrumbs, base_url=base_url)
    resource_path = get_hx_url(breadcrumbs)
    return BlogPost(
        title=title,
        date=(yield from _parse_date(md_file_decomposed.metadata)),
        thumbnail=(yield from _parse_thumbnail(md_file_decomposed.metadata)),
        contents=_md_to_html(md_file_decomposed.content),
        base_url=HttpUrl(base_url),
        resource_path=resource_path,
        url=url,
        targets=TargetFiles(
            complete=Template(
                destination=get_push_url(crumb=breadcrumbs, base_url=''),
                template=breadcrumbs.targets.complete.template,
                extension=breadcrumbs.targets.complete.extension,
            ),
            hx=Template(
                destination=get_hx_url(crumb=breadcrumbs),
                template=breadcrumbs.targets.hx.template,
                extension=breadcrumbs.targets.hx.extension,
            ),
        ),
        reading_time=_estimate_reading_time(md_file_decomposed.content),
        breadcrumbs=breadcrumbs,
        opengraph=(
            yield from create_opengraph_typed_article(
                data=md_file_decomposed,
                url=url,
            )
        ),
        article_opengraph=(
            yield from create_opengraph_article(
                data=md_file_decomposed,
            )
        ),
    )
