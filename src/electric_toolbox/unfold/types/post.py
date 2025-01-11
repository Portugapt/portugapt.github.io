"""Model for unfolded post."""

from expression import Nothing, Ok, Option, Result, Some
from expression.collections import Block
from pydantic import BaseModel, ConfigDict, Field

from electric_toolbox.unfold.types.entities import PluralEntity

from .common import Author, HeaderExtra, OpenGraph, StageType


def default_author() -> Result[Block[Author], Exception]:
    """Default author."""
    return Ok(
        Block.of_seq(
            [
                Author(
                    first_name='João',
                    last_name='Monteiro',
                    username='Portugapt',
                    gender='male',
                    email=Some('monteiro (dot) joao (dot) ps (at) gmail (dot) com'),
                    url=Nothing,
                )
            ]
        )
    )


class PostOpenGraph(BaseModel):
    """Article OpenGraph data."""

    publication_time: str  # iso8601
    modified_time: str  # iso8601
    expiration_time: str  # iso8601
    authors: Block[Author]
    section: str
    tags: Block[str]


class FrontMatter(BaseModel):
    """Front matter data."""

    opengraph: OpenGraph
    post_opengraph: PostOpenGraph
    stage: StageType = 'draft'
    thumbnail: Option[str] = Field(default=Nothing)
    summary: Option[str] = Field(default=Nothing)


class Post(BaseModel):
    """Post data."""

    model_config = ConfigDict(frozen=True)
    file_path: str
    slug: str  # Add the slug to the metadata
    reading_time: str
    contents: str
    head_extras: Option[Block[HeaderExtra]] = Field(default=Nothing)
    front_matter: FrontMatter


class PostsIndex(PluralEntity[Post]):
    """Index of the posts.

    Has the url in breadcrumbs.
    """

    pass


PostsIndex.model_rebuild()

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
