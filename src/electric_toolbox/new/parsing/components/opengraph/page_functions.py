"""Opengraph functions for the whole page. (Non specific)."""

from typing import Any, Generator

import frontmatter  # type: ignore
from expression import Error, Nothing, Ok, Option, Result, Some, effect
from expression.collections import Block
from pydantic import HttpUrl, ValidationError

from electric_toolbox.new.exceptions import ParsingError

from .models import OpenGraph, ViewModelOpenGraph

MarkdownMetadata = dict[str, Any]


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
    else:
        return Error(
            ParsingError(
                message='Title not found',
                cause=ValueError(),
                context={
                    'function': 'electric_toolbox.new.parsing.components.opengraph.page_functions._parse_title',
                },
            )
        )


def _parse_image(data: MarkdownMetadata) -> Result[str, Exception]:
    """Parses the image from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[str, Exception]: Ok(str) containing the image if present and valid,
            Error(Exception) if the image is invalid.
    """
    image = data.get('image', False)
    if image:
        return Ok(image if isinstance(image, str) else image.get('src', ''))
    else:
        return Error(Exception('Image not found'))


def _parse_language(data: MarkdownMetadata, default: str = 'en') -> Result[str, Exception]:
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


def _parse_description(data: MarkdownMetadata) -> Result[Option[str], Exception]:
    """Parses the description from the post's metadata.

    Args:
        data: The metadata dictionary.

    Returns:
        Result[Option[str], Exception]: Ok(Option[str]) containing the description if present and valid,
            Error(Exception) if the description is invalid.
    """
    description = data.get('description', Nothing)
    match description:
        case str(desc):
            return Ok(Some(desc))
        case Option(none=None):
            return Ok(Nothing)
        case _:
            return Error(Exception('Description must be a string'))


@effect.result[OpenGraph, Exception]()
def create_opengraph_typed_article(
    data: frontmatter.Post,
    url: str,
) -> Generator[Any, Any, OpenGraph]:
    """Parses the OpenGraph metadata from the post's metadata.

    Args:
        data: The metadata dictionary.
        url: The URL of the post.

    Returns:
        Result[OpenGraph, Exception]: Ok(OpenGraph) if the metadata is valid
        Error(Exception) otherwise.
    """
    return OpenGraph(
        title=(yield from _parse_title(data.metadata)),
        ogtype='article',
        image=(yield from _parse_image(data.metadata)),
        locale=(yield from _parse_language(data.metadata)),
        description=(yield from _parse_description(data.metadata)),
        url=HttpUrl(url),
    )


def create_opengraph_typed_website(
    title: str,
    image: str,
    locale: str,
    description: str,
    url: str,
) -> Result[OpenGraph, Exception]:
    """Creates an OpenGraph object for a website.

    Args:
        title (str): The title of the website.
        image (str): The image of the website.
        locale (str): The locale of the website.
        description (str): The description of the website.
        url (str): The URL of the website.

    Returns:
        Result[OpenGraph, Exception]: _description_
    """
    try:
        return Ok(
            OpenGraph(
                title=title,
                ogtype='website',
                image=image,
                locale=locale,
                description=Some(description),
                url=HttpUrl(url),
            )
        )
    except ValidationError as e:
        return Error(e)


def _render_meta_tag(property: str, content: str) -> str:
    """Renders a single meta tag."""
    return f'<meta property="{property}" content="{content}">'


def _render_optional_tag(property: str, content: Option[str]) -> Block[str]:
    """Renders a single meta tag if the content is defined."""
    match content:
        case Option(tag='some', some=value):
            return Block.of_seq([_render_meta_tag(property, value)])
        case _:
            return Block.empty()


def _render_open_graph(og: OpenGraph) -> Block[str]:
    """Renders an OpenGraph object into a Block of meta tags."""
    lines = Block.of_seq(
        [
            _render_meta_tag('og:title', og.title),
            _render_meta_tag('og:type', og.ogtype),
            _render_meta_tag('og:image', og.image),
            _render_meta_tag('og:url', str(og.url)),
            _render_meta_tag('og:locale', og.locale),
        ]
    )

    optional_lines = Block.empty()
    optional_lines = optional_lines + _render_optional_tag('og:audio', og.audio)
    optional_lines = optional_lines + _render_optional_tag('og:description', og.description)
    optional_lines = optional_lines + _render_optional_tag('og:determiner', og.determiner)
    optional_lines = optional_lines + _render_optional_tag('og:site_name', og.site_name)
    optional_lines = optional_lines + _render_optional_tag('og:video', og.video)

    match og.locale_alternate:
        case Option(tag='some', some=alternates):
            alternate_locales = alternates.map(lambda x: _render_meta_tag('og:locale:alternate', x))
        case _:
            alternate_locales = Block.empty()

    return lines + optional_lines + alternate_locales


def create_opengraph_view_model(og: OpenGraph) -> ViewModelOpenGraph:
    """Converts an OpenGraph to a ViewModelOpenGraph.

    Args:
        og: The OpenGraph to convert.

    Returns:
        ViewModelOpenGraph: The view model representation.
    """
    return ViewModelOpenGraph(parts=_render_open_graph(og))
