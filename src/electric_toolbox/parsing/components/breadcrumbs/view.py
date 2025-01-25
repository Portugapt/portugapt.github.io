"""Functions to create a breadcrumb view model."""

import json
from typing import List

from expression import Option, Some

from .internal_functions import get_hx_url, get_push_url
from .models import Breadcrumbs, ViewModelBreadcrumb, ViewModelBreadcrumbItem
from .seo import to_json_ld


def prepare_breadcrumbs_view_model_items(
    current: Option[Breadcrumbs],
    base_url: str,
    acc: List[ViewModelBreadcrumbItem],
) -> List[ViewModelBreadcrumbItem]:
    """Creates a breadcrumb view model item from a breadcrumb."""
    match current:
        case Option(tag='some', some=crumb):
            return prepare_breadcrumbs_view_model_items(
                crumb.previous_crumb,
                base_url if not crumb.path.startswith('http') else '',
                [
                    ViewModelBreadcrumbItem(
                        name=crumb.title,
                        push_url=get_push_url(crumb=crumb, base_url=''),
                        get_resource=get_hx_url(crumb=crumb),  # WIP - this is a hack to get the resource path
                        url=get_push_url(crumb=crumb, base_url=base_url),
                    ),
                    *acc,
                ],
            )
        case _:
            return acc


def create_breadcrumbs_view_model(
    crumb: Breadcrumbs,
    base_url: str,
    show_root_item: bool = True,
    separator: str = '/',
) -> ViewModelBreadcrumb:
    """Creates a breadcrumbs view model from a breadcrumb."""
    items = prepare_breadcrumbs_view_model_items(current=Some(crumb), base_url=base_url, acc=[])

    _items = items[1:] if not show_root_item else items
    return ViewModelBreadcrumb(
        items=_items,
        json_ld=json.dumps(to_json_ld(crumb, base_url=base_url)),
        show_root_item=show_root_item,
        separator=separator,
    )
