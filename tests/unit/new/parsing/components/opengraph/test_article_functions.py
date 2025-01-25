# tests/unit/unfold/components/opengraph/test_article_functions.py
"""Tests for article_functions."""

from datetime import datetime, timedelta
from typing import Any, Dict

import frontmatter  # type: ignore
from expression import Ok
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.parsing.components.opengraph.article_functions import (
    _parse_author,
    _parse_authors,
    _parse_publication_time,
    _parse_section,
    _parse_tags,
    create_opengraph_article,
    create_opengraph_article_view_model,
    default_author,
)
from electric_toolbox.parsing.components.opengraph.models import (
    Author,
    OpenGraphArticle,
    ViewModelOpenGraph,
)


def test_default_author_returns_ok() -> None:
    """Test that default_author returns an Ok result."""
    result = default_author()
    assert result.is_ok()


def test_default_author_contains_author() -> None:
    """Test that default_author result contains an Author object."""
    result = default_author().ok
    assert isinstance(result, Block)
    assert len(result) == 1
    author = result.head()
    assert isinstance(author, Author)


def test_parse_author_valid() -> None:
    """Test _parse_author with valid author data."""
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'johndoe',
        'url': HttpUrl('https://example.com/johndoe'),
    }
    expected = Author(**data)  # type: ignore
    actual = _parse_author(data)
    assert actual == Ok(expected)


def test_parse_author_invalid() -> None:
    """Test _parse_author with invalid author data."""
    data = {'invalid_field': 'invalid'}
    actual = _parse_author(data)
    assert actual.is_error()


def test_parse_authors_valid() -> None:
    """Test _parse_authors with valid authors data."""
    data = {
        'authors': [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'johndoe',
                'url': HttpUrl('https://example.com/author1'),
            },
            {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'username': 'janedoe',
                'gender': 'female',
                'url': HttpUrl('https://example.com/author2'),
            },
        ]
    }
    expected = Block.of_seq(
        [
            Author(
                first_name='John',
                last_name='Doe',
                username='johndoe',
                gender='male',
                url=HttpUrl('https://example.com/author1'),
            ),
            Author(
                first_name='Jane',
                last_name='Doe',
                username='janedoe',
                gender='female',
                url=HttpUrl('https://example.com/author2'),
            ),
        ]
    )
    actual = _parse_authors(data)
    assert actual == Ok(expected)


def test_parse_authors_invalid() -> None:
    """Test _parse_authors with invalid authors data."""
    data = {'authors': [{'invalid_field': 'invalid'}]}
    actual = _parse_authors(data)
    assert actual.is_error()


def test_parse_authors_empty() -> None:
    """Test _parse_authors with empty authors data."""
    data: Dict[str, Any] = {}
    actual = _parse_authors(data)
    assert actual.is_ok()
    assert len(actual.ok) == 1
    author = actual.ok.head()
    assert isinstance(author, Author)


def test_parse_publication_time_valid() -> None:
    """Test _parse_publication_time with a valid publication time."""
    data = {'publication_time': datetime(2023, 1, 1, 12, 0, 0)}
    expected = Ok('2023-01-01T12:00:00')
    actual = _parse_publication_time(data)
    assert actual == expected


def test_parse_publication_time_invalid() -> None:
    """Test _parse_publication_time with an invalid publication time."""
    data = {'publication_time': 'invalid'}
    actual = _parse_publication_time(data)
    assert actual.is_error()


def test_parse_publication_time_timedelta() -> None:
    """Test _parse_publication_time with a valid publication time and timedelta."""
    data = {'publication_time': datetime(2023, 1, 1, 12, 0, 0)}
    expected = Ok('2023-01-02T12:00:00')
    actual = _parse_publication_time(data, timedelta(days=1))
    assert actual == expected


def test_parse_tags_valid() -> None:
    """Test _parse_tags with valid tags."""
    data = {'tags': ['tag1', 'tag2']}
    expected = Ok(Block.of_seq(['tag1', 'tag2']))
    actual = _parse_tags(data)
    assert actual == expected


def test_parse_tags_invalid() -> None:
    """Test _parse_tags with invalid tags."""
    data = {'tags': 'invalid'}
    actual = _parse_tags(data)
    assert actual.is_error()


def test_parse_tags_empty() -> None:
    """Test _parse_tags with empty tags."""
    data: Dict[str, Any] = {}
    expected = Ok(Block.empty())
    actual = _parse_tags(data)
    assert actual == expected


def test_parse_section_valid() -> None:
    """Test _parse_section with a valid section."""
    data = {'section': 'example'}
    expected = Ok('example')
    actual = _parse_section(data)
    assert actual == expected


def test_parse_section_empty() -> None:
    """Test _parse_section with an empty section."""
    data: Dict[str, Any] = {}
    actual = _parse_section(data)
    assert actual.is_error()


def test_article_from_md_front_matter_valid() -> None:
    """Test article_from_md_front_matter with valid front matter."""
    data = frontmatter.loads(
        """---
title: "Example Post"
publication_time: 2023-01-01T12:00:00
authors:
    - first_name: "John"
      last_name: "Doe"
      username: "johndoe"
      url: "https://example.com/author1"
    - first_name: "Jane"
      last_name: "Doe"
      username: "janedoe"
      gender: "female"
      url: "https://example.com/author2"
tags:
    - tag1
    - tag2
section: "example"
---
# Example Post
"""
    )
    expected = Ok(
        OpenGraphArticle(
            publication_time='2023-01-01T12:00:00',
            modified_time='2023-01-01T12:00:00',
            expiration_time='2025-01-01T12:00:00',
            authors=Block.of_seq(
                [
                    Author(
                        first_name='John',
                        last_name='Doe',
                        username='johndoe',
                        gender='male',
                        url=HttpUrl('https://example.com/author1'),
                    ),
                    Author(
                        first_name='Jane',
                        last_name='Doe',
                        username='janedoe',
                        gender='female',
                        url=HttpUrl('https://example.com/author2'),
                    ),
                ]
            ),
            section='example',
            tags=Block.of_seq(['tag1', 'tag2']),
        )
    )
    actual = create_opengraph_article(data)
    assert actual == expected


def test_article_from_md_front_matter_invalid() -> None:
    """Test article_from_md_front_matter with invalid front matter."""
    data = frontmatter.loads(
        """---
invalid_field: "This should cause an error"
---
# Invalid Front Matter
"""
    )
    actual = create_opengraph_article(data)
    assert actual.is_error()


def test_to_view_model_valid_article() -> None:
    """Test to_view_model with a valid OpenGraphArticle."""
    article = OpenGraphArticle(
        publication_time='2023-01-01T12:00:00',
        modified_time='2023-01-01T15:30:00',
        expiration_time='2024-01-01T00:00:00',
        authors=Block.of_seq(
            [
                Author(
                    first_name='John',
                    last_name='Doe',
                    username='johndoe',
                    gender='male',
                    url=HttpUrl('https://example.com/author1'),
                ),
                Author(
                    first_name='Jane',
                    last_name='Doe',
                    username='janedoe',
                    gender='female',
                    url=HttpUrl('https://example.com/author2'),
                ),
            ]
        ),
        section='Technology',
        tags=Block.of_seq(['AI', 'Machine Learning']),
    )

    expected_parts = Block.of_seq(
        [
            '<meta property="og:article:published_time" content="2023-01-01T12:00:00">',
            '<meta property="og:article:modified_time" content="2023-01-01T15:30:00">',
            '<meta property="og:article:expiration_time" content="2024-01-01T00:00:00">',
            '<meta property="og:article:section" content="Technology">',
            '<meta property="og:article:author" content="https://example.com/author1">',
            '<meta property="og:article:author" content="https://example.com/author2">',
            '<meta property="og:article:tag" content="AI">',
            '<meta property="og:article:tag" content="Machine Learning">',
        ]
    )

    expected = ViewModelOpenGraph(parts=expected_parts)
    actual = create_opengraph_article_view_model(article)
    assert actual == expected
