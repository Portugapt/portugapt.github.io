"""Build SEO head metadata: canonical, description, Twitter cards, JSON-LD.

These helpers are pure: they turn already-parsed values into the exact strings
emitted in the page ``<head>``. Site-wide identity (author/publisher/site name)
comes from :class:`WebsiteInfo`; per-page values are passed in explicitly and
always take precedence.
"""

import json
from html import escape
from typing import Any, Dict, List, Optional

from expression.collections import Block

from electric_toolbox.configs import SiteAuthor, WebsiteInfo
from electric_toolbox.parsing.components.opengraph import Author

from .models import HeadMeta


def _meta(name: str, content: str) -> str:
    """Render a ``name``-keyed meta tag (used by description / Twitter cards)."""
    return f'<meta name="{name}" content="{escape(content, quote=True)}">'


def _meta_property(prop: str, content: str) -> str:
    """Render a ``property``-keyed meta tag (used by Open Graph)."""
    return f'<meta property="{prop}" content="{escape(content, quote=True)}">'


def _link(rel: str, href: str) -> str:
    """Render a ``<link>`` tag."""
    return f'<link rel="{rel}" href="{escape(href, quote=True)}">'


def _json_ld(obj: Dict[str, Any]) -> str:
    """Render a JSON-LD ``<script>`` block, neutralising any ``</script>``."""
    payload = json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')
    return f'<script type="application/ld+json">{payload}</script>'


def _person_node(author: SiteAuthor) -> Dict[str, Any]:
    """A schema.org ``Person`` node for the site owner."""
    node: Dict[str, Any] = {
        '@type': 'Person',
        'name': author.full_name,
        'url': author.url,
    }
    if author.same_as:
        node['sameAs'] = list(author.same_as)
    return node


def _author_node(author: Author) -> Dict[str, Any]:
    """A schema.org ``Person`` node for an article author."""
    return {
        '@type': 'Person',
        'name': f'{author.first_name} {author.last_name}'.strip(),
        'url': str(author.url),
    }


def _publisher_node(website_info: WebsiteInfo) -> Optional[Dict[str, Any]]:
    """A schema.org ``Organization`` node for the publisher, if configured."""
    if website_info.publisher is None:
        return None
    node: Dict[str, Any] = {'@type': 'Organization', 'name': website_info.publisher.name}
    if website_info.publisher.logo:
        node['logo'] = {'@type': 'ImageObject', 'url': website_info.publisher.logo}
    return node


def website_json_ld(website_info: WebsiteInfo, base_url: str) -> Dict[str, Any]:
    """Build the site-level ``WebSite`` + ``Person`` (+ ``Organization``) graph."""
    graph: List[Dict[str, Any]] = [
        {
            '@type': 'WebSite',
            'url': base_url,
            'name': website_info.site_name,
            'description': website_info.description,
        },
        _person_node(website_info.author),
    ]
    org = _publisher_node(website_info)
    if org is not None:
        graph.append(org)
    return {'@context': 'https://schema.org', '@graph': graph}


def blogposting_json_ld(  # noqa: PLR0913
    *,
    title: str,
    description: Optional[str],
    image: Optional[str],
    url: str,
    date_published: str,
    date_modified: str,
    locale: str,
    authors: Block[Author],
    tags: Block[str],
    website_info: WebsiteInfo,
) -> Dict[str, Any]:
    """Build a schema.org ``BlogPosting`` node for an article."""
    node: Dict[str, Any] = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'headline': title,
        'url': url,
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'datePublished': date_published,
        'dateModified': date_modified,
        'inLanguage': locale,
        'author': [_author_node(a) for a in authors] or [_person_node(website_info.author)],
    }
    if description:
        node['description'] = description
    if image:
        node['image'] = image
    if len(tags) > 0:
        node['keywords'] = list(tags)
    publisher = _publisher_node(website_info)
    if publisher is not None:
        node['publisher'] = publisher
    return node


def build_head_meta(  # noqa: PLR0913
    *,
    title: str,
    description: Optional[str],
    canonical: str,
    image: Optional[str],
    website_info: WebsiteInfo,
    twitter_card: str = 'summary_large_image',
    json_ld_objects: Optional[List[Dict[str, Any]]] = None,
) -> HeadMeta:
    """Assemble the canonical link, description, Twitter card and JSON-LD.

    Open Graph tags are produced separately by the opengraph component; this
    covers everything else a page needs in ``<head>`` for SEO and social.
    """
    parts: List[str] = [_link('canonical', canonical)]
    if description:
        parts.append(_meta('description', description))
    parts.append(_meta_property('og:site_name', website_info.site_name))
    parts.append(_meta('twitter:card', twitter_card))
    parts.append(_meta('twitter:title', title))
    if description:
        parts.append(_meta('twitter:description', description))
    if image:
        parts.append(_meta('twitter:image', image))
    if website_info.twitter:
        parts.append(_meta('twitter:site', website_info.twitter))
    for obj in json_ld_objects or []:
        parts.append(_json_ld(obj))
    return HeadMeta(parts=Block.of_seq(parts))
