"""Tests for the blog section functions."""

from pathlib import Path

import pytest
from expression import Nothing, Some
from expression.collections import Block
from pydantic import HttpUrl

from electric_toolbox.configs import ConfigSettings, FileData, ReadFromPlural, Section, SiteConfigs, WebsiteInfo
from electric_toolbox.parsing.components.breadcrumbs import (
    Breadcrumbs,
)
from electric_toolbox.parsing.components.navigation import create_navigation_menu
from electric_toolbox.parsing.components.opengraph.models import (
    Author,
    OpenGraph,
    OpenGraphArticle,
)
from electric_toolbox.parsing.sections.blog import read_blog


@pytest.fixture
def sample_site_configs(tmp_path: Path) -> SiteConfigs:
    """Sample SiteConfigs for testing."""
    # Create a dummy file in the temporary directory for the blog section
    blog_file = tmp_path / 'blog_post.md'
    blog_file_content = """---
title: "Sample Blog Post"
date: 2023-01-15
image: https://example.com/image.jpg
publication_time: 2023-01-15T09:00:00
modified_time: 2023-01-16T10:00:00
expiration_time: 2025-01-15T09:00:00
authors:
    - first_name: "John"
      last_name: "Doe"
      username: "johndoe"
      gender: "male"
      url: "https://example.com/author1"
section: "Technology"
tags:
    - tech
    - programming
---

# Sample Blog Post
This is a sample blog post content.
"""

    return SiteConfigs(
        settings=ConfigSettings(include_drafts=True),
        base_url='https://example.com',
        website=WebsiteInfo(
            title='Example Website',
            description='Description',
            image='https://example.com/image.png',
            locale='en_US',
        ),
        sections={
            'blog': Section(
                title='Blog',
                description='My blog posts',
                resource_path='/blog',
                read_from=ReadFromPlural(
                    type='plural',
                    path=str(tmp_path),
                    files=Block.of_seq(
                        [
                            FileData(
                                path=blog_file,
                                file_name=blog_file.name,
                                contents=blog_file_content,
                            ),
                        ]
                    ),
                ),
            ),
            'about': Section(
                title='About',
                description='About section',
                resource_path='/about',
                read_from=ReadFromPlural(
                    type='plural',
                    path=str(tmp_path),
                    files=Block.of_seq([]),
                ),
            ),
        },
    )


def test_read_blog_valid(sample_site_configs: SiteConfigs) -> None:
    """Test read_blog with a valid configuration and existing file."""
    result = read_blog(
        sections=sample_site_configs.sections,
        previous_crumb=Some(Breadcrumbs(path='/', title='Home')),
        base_url='https://example.com',
        section='blog',
    )

    assert result.is_ok()
    blog = result.ok

    # Check breadcrumbs
    assert blog.breadcrumbs.title == 'Blog'
    assert blog.breadcrumbs.path == '/blog'
    assert blog.breadcrumbs.previous_crumb == Some(Breadcrumbs(path='/', title='Home'))

    # Check targets
    assert blog.targets.complete.destination == '/blog'
    assert blog.targets.hx.destination == '/blog_hx'

    # Check navigation
    assert blog.navigation == create_navigation_menu(
        sections=sample_site_configs.sections,
        requester_section='Blog',
        base_url='https://example.com',
    )

    # Check posts
    assert len(blog.posts) == 1
    post = blog.posts.head()

    assert post.title == 'Sample Blog Post'
    assert post.date == '2023-01-15T09:00:00'
    assert post.contents == '<h1>Sample Blog Post</h1>\n<p>This is a sample blog post content.</p>'
    assert post.reading_time == '1 min'

    # Check breadcrumbs in post
    assert post.breadcrumbs.title == 'Sample Blog Post'
    assert post.breadcrumbs.path == 'blog-post'
    assert post.breadcrumbs.previous_crumb == Some(
        Breadcrumbs(
            path='/blog',
            title='Blog',
            previous_crumb=Some(Breadcrumbs(path='/', title='Home')),
        )
    )

    # Check opengraph in post
    assert post.opengraph == OpenGraph(
        title='Sample Blog Post',
        ogtype='article',
        image='https://example.com/image.jpg',
        url=HttpUrl('https://example.com/blog/blog-post'),
        locale='en',
        description=Nothing,
    )

    # Check article_opengraph in post
    assert post.article_opengraph == OpenGraphArticle(
        publication_time='2023-01-15T09:00:00',
        modified_time='2023-01-16T10:00:00',
        expiration_time='2025-01-15T09:00:00',
        authors=Block.of_seq(
            [
                Author(
                    first_name='John',
                    last_name='Doe',
                    username='johndoe',
                    gender='male',
                    url=HttpUrl('https://example.com/author1'),
                )
            ]
        ),
        section='Technology',
        tags=Block.of_seq(['tech', 'programming']),
    )


def test_read_blog_invalid_section(sample_site_configs: SiteConfigs) -> None:
    """Test read_blog with an invalid section name."""
    with pytest.raises(KeyError):
        read_blog(
            sections=sample_site_configs.sections,
            previous_crumb=Some(Breadcrumbs(path='/', title='Home')),
            base_url='https://example.com',
            section='invalid',  # type: ignore
        )
