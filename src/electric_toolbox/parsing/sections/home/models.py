"""Home Models."""

from pydantic import BaseModel, ConfigDict, HttpUrl

from electric_toolbox.parsing.common import TargetFiles
from electric_toolbox.parsing.components.navigation import NavigationMenu, ViewModelNavigationMenu
from electric_toolbox.parsing.components.opengraph import OpenGraph, ViewModelOpenGraph
from electric_toolbox.parsing.components.seo import HeadMeta


class HomePage(BaseModel):
    """Home page data."""

    model_config = ConfigDict(frozen=True)
    title: str
    resource_path: str
    targets: TargetFiles
    contents: str
    navigation: NavigationMenu
    opengraph: OpenGraph
    base_url: HttpUrl
    seo: HeadMeta = HeadMeta()


class ViewModelHomePage(BaseModel):
    """Homepage view data."""

    title: str
    resource_path: str
    targets: TargetFiles
    contents: str
    navigation: ViewModelNavigationMenu
    opengraph: ViewModelOpenGraph
    base_url: HttpUrl
    seo: HeadMeta = HeadMeta()
