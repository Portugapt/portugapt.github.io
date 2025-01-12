from typing import Dict, List, Optional

from expression.collections import Block
from pydantic import BaseModel, ConfigDict, HttpUrl

from electric_toolbox.unfold.components.breadcrumbs import Breadcrumbs, ViewModelBreadcrumb
from electric_toolbox.unfold.components.opengraph import OpenGraph, OpenGraphArticle, ViewModelOpenGraph


class BlogPost(BaseModel):
    """Post data."""

    model_config = ConfigDict(frozen=True)
    title: str
    date: str  # iso8601
    base_url: HttpUrl
    url: HttpUrl
    contents: str
    reading_time: str
    breadcrumbs: Breadcrumbs
    opengraph: OpenGraph
    article_opengraph: OpenGraphArticle


class Blog(BaseModel):
    """Blog data."""

    breadcrumbs: Breadcrumbs
    posts: Block[BlogPost]


class Publisher(BaseModel):
    """Publisher data."""

    type: str = 'Organization'
    name: str
    logo: Optional[str] = None


class ArticleSchema(BaseModel):
    """Schema.org Article data."""

    context: str = 'https://schema.org'
    type: str = 'Article'
    headline: str
    image: Optional[str] = None
    author: List[Dict[str, str]]
    datePublished: str
    dateModified: str
    publisher: Publisher
    mainEntityOfPage: Optional[str] = None


class ViewModelBlogPost(BaseModel):
    """Post data."""

    model_config = ConfigDict(frozen=True)
    title: str
    date: str  # iso8601
    contents: str
    base_url: str
    url: str
    reading_time: str
    breadcrumbs: ViewModelBreadcrumb
    opengraph: ViewModelOpenGraph
    article_opengraph: ViewModelOpenGraph
