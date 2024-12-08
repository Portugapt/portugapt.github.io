"""Website structured data."""

from typing import Dict

from expression import Nothing, Option
from expression.collections import Block
from pydantic import BaseModel, ConfigDict, Field


class Head(BaseModel):
    """Head data."""

    model_config = ConfigDict(frozen=True)
    title: str


class HeaderExtra(BaseModel):
    """An header extra."""

    model_config = ConfigDict(frozen=True)
    tag: str
    value: str

    def __str__(self) -> str:
        """To string."""
        return f'<{self.tag}>{self.value}</{self.tag}>'


class Index(BaseModel):
    """Homepage data."""

    model_config = ConfigDict(frozen=True)
    contents: str
    head_extras: Option[Block[HeaderExtra]] = Field(default=Nothing)


class Post(BaseModel):
    """Post data."""

    model_config = ConfigDict(frozen=True)
    contents: str
    head_extras: Option[Block[HeaderExtra]] = Field(default=Nothing)


class WebsiteMatadata(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)
    head: Head
    index: Index
    posts: Dict[str, Post]
