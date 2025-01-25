"""SEO-related utilities for blog posts."""

import json

from .models import ArticleSchema, BlogPost, Publisher


def article_to_json_ld(post: BlogPost, base_url: str) -> str:
    """Generates the JSON-LD representation of an Article from a BlogPost.

    Args:
        post: The BlogPost object.
        base_url: The base URL of the site.

    Returns:
        The JSON-LD string.
    """
    article_schema = ArticleSchema(
        headline=post.title,
        image=post.opengraph.image,
        author=[
            {
                '@type': 'Person',
                'name': author.first_name,
                'url': str(
                    author.url,
                ),
            }
            for author in post.article_opengraph.authors
        ],
        datePublished=post.article_opengraph.publication_time,
        dateModified=post.article_opengraph.modified_time,
        publisher=Publisher(
            name='Your Organization Name',  # Replace with your actual info
            logo='https://example.com/logo.png',  # Replace with your actual logo URL
        ),
        mainEntityOfPage=base_url,
    )

    return json.dumps(article_schema.model_dump(exclude_none=True))
