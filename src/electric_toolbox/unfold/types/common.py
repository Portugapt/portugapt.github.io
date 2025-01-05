"""Common types for metadata."""

from typing import Literal, Optional

from expression import Nothing, Option
from pydantic import BaseModel, ConfigDict, Field


class HeaderExtra(BaseModel):
    """An header extra."""

    model_config = ConfigDict(frozen=True)
    tag: str
    value: str

    def __str__(self) -> str:
        """To string."""
        return f'<{self.tag}>{self.value}</{self.tag}>'


class OpenGraph(BaseModel):
    """OpenGraph data."""

    model_config = ConfigDict(frozen=True)
    title: str
    ogtype: str
    image: str
    locale: str
    description: Option[str] = Field(default=Nothing)
    site_name: Option[str] = Field(default=Nothing)
    url: Option[str] = Field(default=Nothing)


class Image(BaseModel):
    """Represents an image."""

    model_config = ConfigDict(frozen=True)
    url: str
    alt_text: str = ''
    title: Optional[str] = None
    caption: Optional[str] = None


class Author(BaseModel):
    """Represents a profile.

    https://ogp.me/#type_profile
    """

    model_config = ConfigDict(frozen=True)
    first_name: str
    last_name: str
    username: str
    gender: Literal['male', 'female']
    email: Option[str] = Field(default=Nothing)
    url: Option[str] = Field(default=Nothing)


ContentType = Literal['blog', 'article', 'tutorial', 'documentation']

StageType = Literal['draft', 'published']
