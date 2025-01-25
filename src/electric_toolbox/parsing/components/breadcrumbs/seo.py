"""Functions for generating SEO-friendly breadcrumbs."""

from typing import Dict, List, Tuple, Union

from expression import Option, Some

from .internal_functions import block_of_paths, generate_url
from .models import Breadcrumbs


def _generate_urls(current: Option[Breadcrumbs], base_url: str, acc: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Recursively generates the URLs for each breadcrumb."""
    match current:
        case Option(tag='some', some=crumb):
            url = generate_url(crumb=crumb, base_url=base_url)
            return _generate_urls(
                crumb.previous_crumb,
                base_url if not crumb.path.startswith('http') else '',
                [(crumb.title, url), *acc],
            )
        case _:
            return acc


def _build_json_ld_recursive(
    crumbs_urls: List[Tuple[str, str]], position: int, acc: List[Dict[str, Union[str, int]]]
) -> List[Dict[str, Union[str, int]]]:
    """Recursively builds the list of ListItems."""
    match crumbs_urls:
        case []:
            return acc
        case [(name, url), *tail]:
            item: Dict[str, Union[str, int]] = {
                '@type': 'ListItem',
                'position': position,
                'name': name,
                'item': url,
            }
            return _build_json_ld_recursive(
                tail,
                position + 1,
                [*acc, item],
            )
        case _:
            return acc


def to_json_ld(crumb: Breadcrumbs, base_url: str = '') -> Dict[str, Union[str, List[Dict[str, Union[str, int]]]]]:
    """Converts the Breadcrumbs to JSON-LD format recursively."""
    match len(block_of_paths(crumb)):
        case 0:
            return {
                '@context': 'https://schema.org',
                '@type': 'BreadcrumbList',
                'itemListElement': [],
            }
        case _:
            return {
                '@context': 'https://schema.org',
                '@type': 'BreadcrumbList',
                'itemListElement': _build_json_ld_recursive(
                    crumbs_urls=_generate_urls(Some(crumb), base_url, []),
                    position=1,
                    acc=[],
                ),
            }
