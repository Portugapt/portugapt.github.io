"""Tests for read_post in article_functions.py."""

from pathlib import Path

import pytest
from expression import Some
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.configs import FileData, WebsiteInfo
from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs
from electric_toolbox.parsing.components.opengraph.models import (
    Author,
    OpenGraph,
    OpenGraphArticle,
)
from electric_toolbox.parsing.sections.blog.article_functions import read_post


@pytest.fixture
def website_info() -> WebsiteInfo:
    """Minimal site identity for the structured data the post builds."""
    return WebsiteInfo(
        title='Example',
        description='An example site',
        image='https://example.com/og.png',
        locale='en_US',
    )


@pytest.fixture
def previous_crumb() -> Breadcrumbs:
    """A `Products` parent crumb (built with targets, like the real code)."""
    return Breadcrumbs(
        path='products',
        title='Products',
        targets=TargetFiles(
            complete=Template(destination='products', template=ExistingTemplates.BLOG_INDEX, extension='html'),
        ),
    )


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


def test_read_post_valid(
    sample_file_data: FileData,
    previous_crumb: Breadcrumbs,
    website_info: WebsiteInfo,
) -> None:
    """Test read_post with a valid FileData object."""
    result = read_post(
        sample_file_data,
        previous_crumb=Some(previous_crumb),
        website_info=website_info,
        base_url='https://example.com',
    )
    assert result.is_ok()
    post = result.ok

    assert post.title == 'Test Post'
    assert post.date == '2023-01-01T12:00:00+00:00'
    assert post.reading_time == '1 min'
    assert post.contents == (
        '<h1 id="test-post">Test Post'
        '<a class="headerlink" href="#test-post" title="Link to this section">&para;</a></h1>\n'
        '<p>This is the content of the test post.</p>'
    )
    assert post.breadcrumbs.title == 'Test Post'
    assert post.breadcrumbs.path == 'test-file'
    # The frontmatter description is surfaced as the card summary.
    assert post.summary == Some('This is a test post')

    assert post.opengraph == OpenGraph(
        title='Test Post',
        ogtype='article',
        image='https://example.com/image.jpg',
        description=Some('This is a test post'),
        locale='en',
        url=HttpUrl('https://example.com/products/test-file.html'),
    )

    assert post.article_opengraph == OpenGraphArticle(
        publication_time='2023-01-01T12:00:00+00:00',
        modified_time='2023-01-01T12:00:00+00:00',
        expiration_time='2025-01-01T12:00:00+00:00',
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


def test_read_post_seo_contains_structured_data(
    sample_file_data: FileData,
    previous_crumb: Breadcrumbs,
    website_info: WebsiteInfo,
) -> None:
    """The post carries BlogPosting + BreadcrumbList JSON-LD and a canonical link."""
    result = read_post(
        sample_file_data,
        previous_crumb=Some(previous_crumb),
        website_info=website_info,
        base_url='https://example.com',
    )
    assert result.is_ok()
    joined = '\n'.join(result.ok.seo.parts)
    assert '"@type": "BlogPosting"' in joined
    assert '"@type": "BreadcrumbList"' in joined
    assert '<link rel="canonical" href="https://example.com/products/test-file.html">' in joined
    assert '<meta name="twitter:card" content="summary_large_image">' in joined


def test_read_post_meta_description_falls_back_to_excerpt(
    previous_crumb: Breadcrumbs,
    website_info: WebsiteInfo,
) -> None:
    """A post without a frontmatter `description` still gets a meta description."""
    file = FileData(
        path=Path('no_desc.md'),
        file_name='no_desc.md',
        contents="""---
title: "No Desc"
publication_time: 2023-01-01T12:00:00
image: "https://example.com/i.jpg"
section: "Example"
---

## Intro

Plain body text that should become the description.
""",
    )
    result = read_post(
        file,
        previous_crumb=Some(previous_crumb),
        website_info=website_info,
        base_url='https://example.com',
    )
    assert result.is_ok()
    joined = '\n'.join(result.ok.seo.parts)
    assert 'name="description"' in joined
    assert 'Plain body text that should become the description.' in joined
