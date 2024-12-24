"""Model for unfolded post."""

from datetime import datetime

from expression import Nothing, Option, Some
from expression.collections import Block
from pydantic import BaseModel, ConfigDict, Field

from .common import Author, ContentType, HeaderExtra, Image, StageType


def default_author() -> Author:
    """Default author."""
    return Author(
        name='João Monteiro',
        email=Some('monteiro (dot) joao (dot) ps (at) gmail (dot) com'),
        url=Nothing,
    )


class FrontMatter(BaseModel):
    """Front matter data."""

    author: Author
    title: str
    language: str = 'en'
    stage: StageType = 'draft'
    publish_date: Option[datetime] = Field(default=Nothing)
    last_update: Option[datetime] = Field(default=Nothing)
    summary: Option[str] = Field(default=Nothing)
    tags: Block[str] = Field(default_factory=Block.empty)
    category: Option[str] = Field(default=Nothing)
    thumbnail: Option[Image] = Field(default=Nothing)
    content_type: ContentType = 'blog'


class Post(BaseModel):
    """Post data."""

    model_config = ConfigDict(frozen=True)
    file_path: str
    slug: str  # Add the slug to the metadata
    reading_time: str
    contents: str
    head_extras: Option[Block[HeaderExtra]] = Field(default=Nothing)
    front_matter: FrontMatter

    # @field_validator('slug', 'title', 'summary', 'category', 'language')
    # def check_not_empty(cls, v: str) -> str:
    #     """Check if the value is not empty."""
    #     if not v:
    #         raise ValueError('must not be empty')
    #     return v

    # @field_validator('date')
    # def check_date_format(cls, v: str) -> str:
    #     """Check if the date is in the correct format. WIP."""
    #     return v

    # @field_validator('author')
    # def check_author_type(cls, v: Union[Author, str]) -> Union[Author, str]:
    #     if not isinstance(v, (Author, str)):
    #         raise ValueError('must be either an Author object or a string')
    #     return v

    # @field_validator('tags', 'head_extras')
    # def check_list_not_empty(cls, v: Block[Any]) -> Block[Any]:
    #     """Check if the list is not empty."""
    #     if v is not Nothing and len(v) == 0:
    #         raise ValueError('must not be an empty list')
    #     return v
