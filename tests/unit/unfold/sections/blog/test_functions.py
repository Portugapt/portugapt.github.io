"""Tests for read_post in posts.py"""

from pathlib import Path

import pytest
from expression import Some
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.common.types.file import FileData
from electric_toolbox.unfold.components.breadcrumbs import Breadcrumbs
from electric_toolbox.unfold.components.opengraph.models import (
    Author,
    OpenGraph,
    OpenGraphArticle,
)
from electric_toolbox.unfold.sections.blog.functions import read_post


@pytest.fixture
def sample_file_data() -> FileData:
    """Sample FileData object for testing."""
    return FileData(
        path=Path('test_file.md'),
        file_name='test_file.md',
        contents="""---
title: "Test Post"
publication_time: 2023-01-01T12:00:00
image: "https://example.com/image.jpg"
description: "This is a test post"
authors:
    - first_name: "John"
      last_name: "Doe"
      username: "johndoe"
      url: "https://example.com/author1"
tags:
    - test
    - example
section: "example"
language: "en"
---

# Test Post

This is the content of the test post.
""",
    )


def test_read_post_valid(sample_file_data: FileData) -> None:
    """Test read_post with a valid FileData object."""
    previous_crumb = Some(Breadcrumbs(path='products', title='Products'))
    result = read_post(
        sample_file_data,
        previous_crumb=previous_crumb,
        base_url='https://example.com',
    )
    assert result.is_ok()
    post = result.ok

    with open('test_file.json', 'w') as f:
        f.write(post.model_dump_json(indent=4))

    assert post.title == 'Test Post'
    assert post.date == '2023-01-01T12:00:00'
    assert post.reading_time == '1 min'
    assert post.contents == '<h1>Test Post</h1>\n<p>This is the content of the test post.</p>'
    assert post.breadcrumbs.title == 'Test Post'
    assert post.breadcrumbs.path == 'test-file'

    assert post.opengraph == OpenGraph(
        title='Test Post',
        ogtype='article',
        image='https://example.com/image.jpg',
        description=Some('This is a test post'),
        locale='en',
        url=HttpUrl('https://example.com/products/test-file'),
    )

    assert post.article_opengraph == OpenGraphArticle(
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
            ]
        ),
        section='example',
        tags=Block.of_seq(['test', 'example']),
    )
