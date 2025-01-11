"""Breadcrumbs component."""

from .internal_functions import block_of_paths, generate_url
from .models import Breadcrumbs
from .seo import to_json_ld

__all__ = ['Breadcrumbs', 'block_of_paths', 'generate_url', 'to_json_ld']
