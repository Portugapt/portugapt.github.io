"""Website structured data."""

from expression.collections import Block
from pydantic import BaseModel, ConfigDict

from electric_toolbox.unfold.types.configs import SiteConfigs

from .post import Post


class WebsiteMatadata(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)

    configs: SiteConfigs
    title: str
    posts: Block[Post]
