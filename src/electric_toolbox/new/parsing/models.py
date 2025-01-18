"""Website models."""

from pydantic import BaseModel, ConfigDict

from .sections.blog import Blog
from .sections.home import HomePage


class Website(BaseModel):
    """Home page data."""

    model_config = ConfigDict(frozen=True)
    homepage: HomePage
    blog: Blog
