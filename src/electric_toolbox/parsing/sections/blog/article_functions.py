"""Functions for parsing blog posts."""

import re
from datetime import datetime, timedelta
from typing import Any, Generator

import frontmatter  # type: ignore
from expression import Error, Nothing, Ok, Option, Result, Some, effect
from markdown import Markdown
from pydantic import HttpUrl
from pymdownx.highlight import HighlightExtension  # type: ignore
from pymdownx.superfences import SuperFencesCodeExtension  # type: ignore
from slugify import slugify

from electric_toolbox.configs import FileData, WebsiteInfo
from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.exceptions import ParsingError
from electric_toolbox.parsing.common import TargetFiles, Template, isoformat_with_tz
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs, get_push_url, to_json_ld
from electric_toolbox.parsing.components.opengraph import (
    OpenGraph,
    OpenGraphArticle,
    create_opengraph_article,
    create_opengraph_typed_article,
)
from electric_toolbox.parsing.components.seo import HeadMeta, blogposting_json_ld, build_head_meta

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
    name_without_extension = file_name.split('.', maxsplit=1)[0]
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
            return Ok(isoformat_with_tz(date_obj + add_time))
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

    Uses the pymdownx ``highlight`` + ``superfences`` pair (the supported
    combination) for Pygments syntax highlighting instead of mixing
    ``codehilite`` with ``superfences``, which fight over fenced blocks.
    Headings get stable slug ids (``toc``) so they can be deep-linked, and
    tables / footnotes / inline HTML are enabled for richer posts.

    Args:
        contents: The Markdown content.

    Returns:
        str: The HTML representation of the Markdown content.
    """
    md = Markdown(
        extensions=[
            'attr_list',
            'tables',
            'footnotes',
            'md_in_html',
            'toc',
            HighlightExtension(css_class='code-block', guess_lang=False, use_pygments=True),
            SuperFencesCodeExtension(css_class='code-block'),
        ],
        extension_configs={
            'toc': {'permalink': True, 'permalink_title': 'Link to this section'},
        },
    )
    return md.convert(contents)


def _option_to_optional(value: Option[str]) -> str | None:
    """Collapses an ``Option[str]`` into a plain ``Optional[str]``."""
    match value:
        case Option(tag='some', some=inner):
            return inner
        case _:
            return None


_HEADING_RE = re.compile(r'^#{1,6}.*$', re.MULTILINE)
_FENCE_RE = re.compile(r'```.*?```', re.DOTALL)
_INLINE_CODE_RE = re.compile(r'`[^`]*`')
_IMAGE_RE = re.compile(r'!\[[^\]]*\]\([^)]*\)')
_LINK_RE = re.compile(r'\[([^\]]*)\]\([^)]*\)')
_MD_SYMBOLS_RE = re.compile(r'[*_>~]')
_WS_RE = re.compile(r'\s+')


def _excerpt(markdown: str, limit: int = 160) -> str:
    """Derive a plain-text summary from markdown for the meta description fallback."""
    text = _FENCE_RE.sub(' ', markdown)
    text = _HEADING_RE.sub(' ', text)
    text = _IMAGE_RE.sub(' ', text)
    text = _LINK_RE.sub(r'\1', text)
    text = _INLINE_CODE_RE.sub(' ', text)
    text = _MD_SYMBOLS_RE.sub('', text)
    text = _WS_RE.sub(' ', text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].rstrip() + '…'


def _build_post_seo(  # noqa: PLR0913
    title: str,
    url: str,
    description: str,
    opengraph: OpenGraph,
    article_opengraph: OpenGraphArticle,
    breadcrumbs: Breadcrumbs,
    website_info: WebsiteInfo,
    base_url: str,
) -> HeadMeta:
    """Assembles canonical/description/Twitter + BlogPosting & BreadcrumbList JSON-LD."""
    post_ld = blogposting_json_ld(
        title=title,
        description=description,
        image=opengraph.image,
        url=url,
        date_published=article_opengraph.publication_time,
        date_modified=article_opengraph.modified_time,
        locale=opengraph.locale,
        authors=article_opengraph.authors,
        tags=article_opengraph.tags,
        website_info=website_info,
    )
    breadcrumb_ld = to_json_ld(breadcrumbs, base_url=base_url)
    return build_head_meta(
        title=title,
        description=description,
        canonical=url,
        image=opengraph.image,
        website_info=website_info,
        twitter_card='summary_large_image',
        json_ld_objects=[post_ld, breadcrumb_ld],
    )


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
    website_info: WebsiteInfo,
    base_url: str = '',
) -> Generator[Any, Any, BlogPost]:
    """Reads a post from a `FileData` object.

    Parses the front matter and converts the Markdown content to HTML.

    Args:
        file: The `FileData` object containing the post file.
        previous_crumb: The previous breadcrumb trail.
        website_info: Site-wide identity used to build the structured data.
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
    resource_path = get_push_url(breadcrumbs, base_url='')
    opengraph = yield from create_opengraph_typed_article(data=md_file_decomposed, url=url)
    article_opengraph = yield from create_opengraph_article(data=md_file_decomposed)
    # Always have a description: frontmatter `description` if present, otherwise
    # a plain-text excerpt of the content (so every page has a meta description).
    description = _option_to_optional(opengraph.description) or _excerpt(md_file_decomposed.content)
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
        ),
        reading_time=_estimate_reading_time(md_file_decomposed.content),
        breadcrumbs=breadcrumbs,
        opengraph=opengraph,
        article_opengraph=article_opengraph,
        summary=opengraph.description,
        seo=_build_post_seo(
            title=title,
            url=url,
            description=description,
            opengraph=opengraph,
            article_opengraph=article_opengraph,
            breadcrumbs=breadcrumbs,
            website_info=website_info,
            base_url=base_url,
        ),
    )
