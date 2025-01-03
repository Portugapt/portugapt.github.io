"""Website structured data."""

from expression.collections import Block
from pydantic import BaseModel, ConfigDict

from .post import Post


class WebsiteMatadata(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)

    title: str
    posts: Block[Post]
