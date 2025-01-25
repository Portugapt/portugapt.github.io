"""Models for navigation."""

from expression.collections import Block
from pydantic import BaseModel, ConfigDict, HttpUrl


class NavigationSection(BaseModel):
    """Represents a navigation menu."""

    model_config = ConfigDict(frozen=True)
    title: str
    base_url: HttpUrl
    path: str
    hx_get: str
    active: bool = False


class NavigationMenu(BaseModel):
    """Navigation Menu model."""

    model_config = ConfigDict(frozen=True)
    sections: Block[NavigationSection]


class ViewModelNavigationMenu(BaseModel):
    """View model for navigation menu."""

    model_config = ConfigDict(frozen=True)
    sections: Block[NavigationSection]
