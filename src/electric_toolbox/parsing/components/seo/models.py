"""Models for the SEO head-metadata component."""

from expression.collections import Block
from pydantic import BaseModel, ConfigDict


class HeadMeta(BaseModel):
    """A bundle of pre-rendered ``<head>`` lines.

    Holds the canonical link, plain meta description, Twitter Card tags and any
    JSON-LD ``<script>`` blocks for a page. Rendered verbatim (``|safe``) inside
    the ``{% block seo %}`` of the base template.
    """

    model_config = ConfigDict(frozen=True)
    parts: Block[str] = Block.empty()
