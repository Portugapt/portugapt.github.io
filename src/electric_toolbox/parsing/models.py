"""Website models."""

from pydantic import BaseModel, ConfigDict

from .sections.blog import Blog, ViewModelBlog
from .sections.home import HomePage, ViewModelHomePage


class Website(BaseModel):
    """Home page data."""

    model_config = ConfigDict(frozen=True)
    homepage: HomePage
    blog: Blog


class ViewModelWebsite(BaseModel):
    """Website view model."""

    model_config = ConfigDict(frozen=True)
    homepage: ViewModelHomePage
    blog: ViewModelBlog
