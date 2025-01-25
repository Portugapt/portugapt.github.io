"""View model for the home page."""

from electric_toolbox.parsing.components.navigation import create_navigation_view_model
from electric_toolbox.parsing.components.opengraph import (
    create_opengraph_view_model,
)

from .models import HomePage, ViewModelHomePage


def create_homepage_view_model(
    homepage: HomePage,
) -> ViewModelHomePage:
    """Prepares the view model for the home page.

    Args:
        homepage: The home page.

    Returns:
        The view model for the home page.
    """
    return ViewModelHomePage(
        title=homepage.title,
        resource_path=homepage.resource_path,
        targets=homepage.targets,
        contents=homepage.contents,
        navigation=create_navigation_view_model(homepage.navigation),
        opengraph=create_opengraph_view_model(homepage.opengraph),
        base_url=homepage.base_url,
    )
