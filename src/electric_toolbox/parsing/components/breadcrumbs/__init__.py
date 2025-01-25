"""Breadcrumbs component."""

from .internal_functions import block_of_paths, get_hx_url, get_push_url
from .models import Breadcrumbs, ViewModelBreadcrumb, ViewModelBreadcrumbItem
from .seo import to_json_ld
from .view import create_breadcrumbs_view_model, prepare_breadcrumbs_view_model_items

__all__ = [
    'Breadcrumbs',
    'ViewModelBreadcrumb',
    'ViewModelBreadcrumbItem',
    'block_of_paths',
    'create_breadcrumbs_view_model',
    'get_hx_url',
    'get_push_url',
    'prepare_breadcrumbs_view_model_items',
    'to_json_ld',
]
