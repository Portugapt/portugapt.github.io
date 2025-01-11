import json
from typing import List

from expression import Option, Some

from .internal_functions import generate_url
from .models import BreadcrumbItemViewModel, Breadcrumbs, BreadcrumbViewModel
from .seo import to_json_ld


def prepare_breadcrumbs_view_model_items(
    current: Option[Breadcrumbs], base_url: str, acc: List[BreadcrumbItemViewModel]
) -> List[BreadcrumbItemViewModel]:
    """Creates a breadcrumb view model item from a breadcrumb."""
    match current:
        case Option(tag='some', some=crumb):
            url = generate_url(crumb=crumb, base_url=base_url)
            return prepare_breadcrumbs_view_model_items(
                crumb.previous_crumb,
                base_url if not crumb.path.startswith('http') else '',
                [BreadcrumbItemViewModel(name=crumb.title, url=url), *acc],
            )
        case _:
            return acc


def prepare_breadcrumbs_view_model(
    crumb: Breadcrumbs,
    base_url: str,
    show_root_item: bool = True,
    separator: str = '/',
) -> BreadcrumbViewModel:
    """Creates a breadcrumbs view model from a breadcrumb."""
    items = prepare_breadcrumbs_view_model_items(current=Some(crumb), base_url=base_url, acc=[])

    _items = items[1:] if not show_root_item else items
    return BreadcrumbViewModel(
        items=_items,
        json_ld=json.dumps(to_json_ld(crumb, base_url=base_url)),
        show_root_item=show_root_item,
        separator=separator,
    )
