"""Breadcrumbs model."""

from typing import Any, List

from expression import Nothing, Option
from pydantic import BaseModel, Field

from electric_toolbox.parsing.common import TargetFiles


class Breadcrumbs(BaseModel):
    """Breadcrumbs for a page. Generic implementation."""

    path: str  # Could be a relative path segment or a full URL
    title: str
    targets: TargetFiles
    data: Option[Any] = Field(default=Nothing)  # Any extra data
    previous_crumb: Option['Breadcrumbs'] = Field(default=Nothing)  # Link to previous breadcrumb (towards the root)


class ViewModelBreadcrumbItem(BaseModel):
    """Breadcrumb item view model."""

    name: str
    url: str
    push_url: str
    get_resource: str


class ViewModelBreadcrumb(BaseModel):
    """Breadcrumbs view model."""

    items: List[ViewModelBreadcrumbItem]
    json_ld: str
    show_root_item: bool = True  # Control visibility of the root item
    separator: str = '/'
