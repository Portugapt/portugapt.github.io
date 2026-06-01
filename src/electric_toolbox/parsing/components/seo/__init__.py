"""SEO head-metadata component (canonical, description, Twitter cards, JSON-LD)."""

from .functions import blogposting_json_ld, build_head_meta, website_json_ld
from .models import HeadMeta

__all__ = [
    'HeadMeta',
    'blogposting_json_ld',
    'build_head_meta',
    'website_json_ld',
]
