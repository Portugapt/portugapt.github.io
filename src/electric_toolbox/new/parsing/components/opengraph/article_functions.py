"""Article functions."""

from datetime import datetime, timedelta
from typing import Any, Dict, Generator

import frontmatter  # type: ignore
from expression import Error, Ok, Result, Some, effect
from expression.collections import Block
from expression.extra.result.traversable import traverse
from pydantic import HttpUrl

from .models import Author, OpenGraphArticle, ViewModelOpenGraph

MarkdownMetadata = dict[str, Any]


def default_author() -> Result[Block[Author], Exception]:
    """Default author."""
    return Ok(
        Block.of_seq(
            [
                Author(
                    first_name='João',
                    last_name='Monteiro',
                    username='Portugapt',
                    url=HttpUrl('https://portugapt.github.io/about'),
                    gender='male',
                    email=Some('monteiro (dot) joao (dot) ps (at) gmail (dot) com'),
                )
            ]
        )
    )


def _parse_publication_time(data: MarkdownMetadata, add_time: timedelta = timedelta(days=0)) -> Result[str, Exception]:
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


def _parse_author(data: Dict[str, Any]) -> Result[Author, Exception]:
    """Parses the author information from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[Author, Exception]: Ok(Author) if the author information is present and valid,
            Error(Exception) otherwise.
    """
    try:
        return Ok(Author(**data))
    except Exception as e:
        return Error(Exception('Author frontmatter incorrect.', e))


@effect.result[Block[Author], Exception]()
def _parse_authors(data: MarkdownMetadata) -> Generator[Any, Any, Block[Author]]:
    """Parses the author information from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[Author, Exception]: Ok(Author) if the author information is present and valid,
            Error(Exception) otherwise.
    """
    if data.get('authors', False):
        return (yield from traverse(_parse_author, Block.of_seq(xs=data['authors'])))
    else:
        return (yield from default_author())


def _parse_tags(data: MarkdownMetadata) -> Result[Block[str], Exception]:
    """Parses the tags from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[Block[str], Exception]: Ok(Block[str]) containing the tags if present and valid,
            Error(Exception) if the tags are invalid.
    """
    tags = data.get('tags')
    if tags is None:
        return Ok(Block[str].empty())
    match tags:
        case list() if all(isinstance(tag, str) for tag in tags):
            return Ok(Block.of_seq(tags))
        case _:
            return Error(Exception('Tags must be a list of strings'))


def _parse_section(
    data: MarkdownMetadata,
) -> Result[str, Exception]:
    """Parses the content type from the post's metadata.

    Args:
        data: The metadata dictionary.
        default: The default content type if not specified in the metadata.

    Returns:
        Result[ContentType, Exception]: Ok(ContentType) containing the content type if present and valid,
            Error(Exception) if the content type is invalid.
    """
    content_type = data.get('section', False)
    if data.get('section', False):
        try:
            return Ok(str(content_type))
        except ValueError:
            return Error(Exception('Invalid content type'))
    return Error(Exception(f'Invalid content type: {content_type}'))


@effect.result[OpenGraphArticle, Exception]()
def article_from_md_front_matter(data: frontmatter.Post) -> Generator[Any, Any, OpenGraphArticle]:
    """Create the OpenGraph for an Article.

    Args:
        data: The frontmatter data.

    Returns:
        OpenGraphArticle: The OpenGraphArticle.
    """
    return OpenGraphArticle(
        publication_time=(yield from _parse_publication_time(data.metadata)),
        modified_time=(yield from _parse_publication_time(data.metadata)),
        expiration_time=(yield from _parse_publication_time(data.metadata, add_time=timedelta(days=731))),
        authors=(yield from _parse_authors(data.metadata)),
        tags=(yield from _parse_tags(data.metadata)),
        section=(yield from _parse_section(data.metadata)),
    )


def _render_author(author: Author) -> str:
    """Renders a single author tag."""
    return f'<meta property="og:article:author" content="{author.url}">'


def _render_tag(tag: str) -> str:
    """Renders a single tag."""
    return f'<meta property="og:article:tag" content="{tag}">'


def _render_article(article: OpenGraphArticle) -> Block[str]:
    """Renders an OpenGraphArticle into a Block of meta tags."""
    lines = Block.of_seq(
        [
            f'<meta property="og:article:published_time" content="{article.publication_time}">',
            f'<meta property="og:article:modified_time" content="{article.modified_time}">',
            f'<meta property="og:article:expiration_time" content="{article.expiration_time}">',
            f'<meta property="og:article:section" content="{article.section}">',
        ]
    )

    author_lines = article.authors.map(_render_author)
    tag_lines = article.tags.map(_render_tag)

    return lines + author_lines + tag_lines


def article_og_to_view_model(article: OpenGraphArticle) -> ViewModelOpenGraph:
    """Converts an OpenGraphArticle to a ViewModelOpenGraphArticle.

    Args:
        article: The OpenGraphArticle to convert.

    Returns:
        ViewModelOpenGraphArticle: The view model representation.
    """
    return ViewModelOpenGraph(parts=_render_article(article))
