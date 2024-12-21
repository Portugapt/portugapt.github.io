"""Unfold posts into canonical format."""

import re
from datetime import datetime
from typing import Any, Generator, Tuple

import frontmatter  # type: ignore
import markdown
from expression import Error, Nothing, Ok, Option, Result, Some, effect
from expression.collections import Block, Map
from expression.extra.result.traversable import traverse
from slugify import slugify

from electric_toolbox.common.types.file import FileData
from electric_toolbox.unfold.types.common import Author, ContentType, StageType
from electric_toolbox.unfold.types.post import FrontMatter, Post, default_author

FileName = str
Content = str
Metadata = dict[str, Any]
WordsPerMinute = int
Minutes = int
Hours = int
Slug = str

ONE_HOUR = 60


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


def _parse_author(data: Metadata) -> Result[Author, Exception]:
    """Parses the author information from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[Author, Exception]: Ok(Author) if the author information is present and valid,
            Error(Exception) otherwise.
    """
    if data.get('author', False):
        try:
            return Ok(Author(**data['author']))
        except Exception as e:
            return Error(Exception('Author frontmatter incorrect.', e))
    else:
        return Ok(default_author())


def _parse_stage(data: Metadata, default: StageType = 'draft') -> Result[StageType, Exception]:
    """Parses the stage (draft, published, etc.) from the post's metadata.

    Args:
        data: The metadata dictionary.
        default: The default stage if not specified in the metadata.

    Returns:
        Result[StageType, Exception]: Ok(StageType) containing the stage if valid,
            Error(Exception) if the stage is invalid.
    """
    stage = data.get('stage', default)
    match stage:
        case 'draft':
            return Ok('draft')
        case 'published':
            return Ok('published')
        case _:
            return Error(Exception(f'Invalid stage: {stage}'))


def _parse_publish_date(data: Metadata) -> Result[Option[datetime], Exception]:
    """Parses the publish date from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[Option[datetime], Exception]: Ok(Option[datetime]) containing the publish date if present and valid,
            Error(Exception) if the publish date is invalid.
    """
    date_obj = data.get('publish_date')
    match date_obj:
        case datetime():
            return Ok(Some(date_obj))
        case None:
            return Ok(Nothing)
        case _:
            return Error(Exception('Publish date must be a datetime object'))


def _parse_title(data: Metadata) -> Result[str, Exception]:
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


def _parse_tags(data: Metadata) -> Result[Block[str], Exception]:
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


def _parse_language(data: Metadata, default: str = 'en') -> Result[str, Exception]:
    """Parses the language from the post's metadata.

    Args:
        data: The metadata dictionary.
        default: The default language if not specified in the metadata.

    Returns:
        Result[str, Exception]: Ok(str) containing the language if present and valid,
            Error(Exception) if the language is invalid.
    """
    language = data.get('language', default)
    if isinstance(language, str):
        return Ok(language)
    return Error(Exception('Language must be a string'))


def _parse_content_type(data: Metadata, default: ContentType = 'blog') -> Result[ContentType, Exception]:
    """Parses the content type from the post's metadata.

    Args:
        data: The metadata dictionary.
        default: The default content type if not specified in the metadata.

    Returns:
        Result[ContentType, Exception]: Ok(ContentType) containing the content type if present and valid,
            Error(Exception) if the content type is invalid.
    """
    content_type = data.get('content_type', default)
    if content_type in ['blog', 'article', 'tutorial', 'documentation']:
        return Ok(content_type)
    return Error(Exception(f'Invalid content type: {content_type}'))


@effect.result[FrontMatter, Exception]()
def _read_frontmatter(data: frontmatter.Post) -> Generator[Any, Any, FrontMatter]:
    """Reads and parses the front matter from a post.

    Args:
        data: The post loaded using the `frontmatter` library.

    Returns:
        Result[FrontMatter, Exception]: Ok(FrontMatter) if the front matter is parsed successfully,
            Error(Exception) if any error occurs during parsing.
    """
    return FrontMatter(
        author=(yield from _parse_author(data.metadata)),
        title=(yield from _parse_title(data.metadata)),
        language=(yield from _parse_language(data.metadata)),
        stage=(yield from _parse_stage(data.metadata)),
        publish_date=(yield from _parse_publish_date(data.metadata)),
        tags=(yield from _parse_tags(data.metadata)),
        content_type=(yield from _parse_content_type(data.metadata)),
    )


def _to_slug(file_name: str) -> Slug:
    """Converts a file name to a URL-friendly slug.

    Args:
        file_name: The input file name.

    Returns:
        Slug: A URL-friendly slug.
    """
    name_without_extension = file_name.split('.')[0]
    _s = slugify(name_without_extension)
    return _s


def _md_to_html(contents: str) -> str:
    """Converts Markdown content to HTML using the `markdown` library.

    Args:
        contents: The Markdown content.

    Returns:
        str: The HTML representation of the Markdown content.
    """
    return markdown.markdown(
        contents,
        extensions=[
            'attr_list',
        ],
    )


@effect.result[Post, Exception]()
def read_post(file: FileData) -> Generator[Any, Any, Post]:
    """Reads a post from a `FileData` object.

    Parses the front matter and converts the Markdown content to HTML.

    Args:
        file: The `FileData` object representing the post file.

    Returns:
        Result[Post, Exception]: Ok(Post) if the post is read and parsed successfully,
            Error(Exception) if any error occurs during reading or parsing.
    """
    unfolded_post: frontmatter.Post = frontmatter.loads(file.contents)
    return Post(
        slug=_to_slug(file.file_name),
        file_path=file.path.as_posix(),
        reading_time=_estimate_reading_time(unfolded_post.content),
        contents=_md_to_html(unfolded_post.content),
        head_extras=Nothing,
        front_matter=(yield from _read_frontmatter(unfolded_post)),
    )


def read_all_posts(files: Map[FileName, FileData]) -> Result[Block[Post], Exception]:
    """Reads all posts from a Map of `FileData` objects.

    Args:
        files: A Map where keys are file names and values are `FileData` objects.

    Returns:
        Result[Map[Slug, Post], Exception]: Ok(Map[str, Post]) if all posts are read successfully,
            Error(Exception) if any error occurs while reading or parsing a post.
    """

    def read_post_effect(
        data: Tuple[FileName, FileData],
    ) -> Result[Post, Exception]:
        """Reads a post from a `FileData` object using an effect."""
        return read_post(data[1])

    return traverse(read_post_effect, files.to_list())
