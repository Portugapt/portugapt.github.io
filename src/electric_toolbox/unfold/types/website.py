"""Website structured data."""

from pydantic import BaseModel, ConfigDict

from electric_toolbox.unfold.types.configs import SiteConfigs

from .post import PostsIndex


class WebsiteMatadata(BaseModel):
    """Website data."""

    model_config = ConfigDict(frozen=True)

    configs: SiteConfigs
    title: str
    posts_section: PostsIndex
