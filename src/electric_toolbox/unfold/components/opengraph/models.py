"""Model for unfolded post."""

from typing import Literal

from expression import Nothing, Option
from expression.collections import Block
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class OpenGraph(BaseModel):
    """OpenGraph data."""

    model_config = ConfigDict(frozen=True)
    title: str
    ogtype: str
    image: str
    url: HttpUrl
    locale: str
    audio: Option[str] = Field(default=Nothing)
    description: Option[str] = Field(default=Nothing)
    determiner: Option[str] = Field(default=Nothing)
    locale_alternate: Option[Block[str]] = Field(default=Nothing)
    site_name: Option[str] = Field(default=Nothing)
    video: Option[str] = Field(default=Nothing)


class Author(BaseModel):
    """Represents a profile.

    https://ogp.me/#type_profile
    """

    model_config = ConfigDict(frozen=True)
    first_name: str
    last_name: str
    username: str
    url: HttpUrl
    gender: Literal['male', 'female'] = 'male'
    email: Option[str] = Field(default=Nothing)


class OpenGraphArticle(BaseModel):
    """Article OpenGraph data."""

    publication_time: str  # iso8601
    modified_time: str  # iso8601
    expiration_time: str  # iso8601
    authors: Block[Author]
    section: str
    tags: Block[str]


ContentType = Literal['blog', 'article', 'tutorial', 'documentation']


class ViewModelOpenGraph(BaseModel):
    """View model for OpenGraphArticle."""

    model_config = ConfigDict(frozen=True)
    parts: Block[str]
