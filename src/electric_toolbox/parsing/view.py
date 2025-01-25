from electric_toolbox.parsing.sections.blog import create_blog_to_view_model
from electric_toolbox.parsing.sections.home import create_homepage_view_model

from .models import ViewModelWebsite, Website


def create_website_view_model(
    website: Website,
) -> ViewModelWebsite:
    """Create a view model for the website.

    Args:
        website: The website to create a view model for.

    Returns:
        The view model for the website.
    """
    return ViewModelWebsite(
        homepage=create_homepage_view_model(website.homepage),
        blog=create_blog_to_view_model(website.blog),
    )
