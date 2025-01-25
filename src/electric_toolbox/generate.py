"""Generation of files."""

from pathlib import Path
from typing import Any, TypedDict

from expression import curry_flip
from jinja2 import Environment, Template

from .constants import ExistingTemplates
from .parsing import Template as InternalTemplate
from .parsing import ViewModelBlog, ViewModelBlogPost, ViewModelHomePage, ViewModelNavigationMenu, ViewModelWebsite


def get_template_function(
    template_type: ExistingTemplates,
    env: Environment,
) -> Template:
    """Retrieves the Jinja2 template based on the enum member.

    Args:
        template_type: The ExistingTemplates enum member.
        env: The Jinja2 environment.

    Returns:
        The Jinja2 template.
    """
    match template_type:
        case ExistingTemplates.INDEX:
            return env.get_template('sections/index/index.html')
        case ExistingTemplates.INDEX_HX:
            return env.get_template('sections/index/_index.html')
        case ExistingTemplates.BLOG_INDEX:
            return env.get_template('sections/blog/index.html')
        case ExistingTemplates.BLOG_INDEX_HX:
            return env.get_template('sections/blog/_index.html')
        case ExistingTemplates.BLOG_ARTICLE:
            return env.get_template('sections/blog/article.html')
        case ExistingTemplates.BLOG_ARTICLE_HX:
            return env.get_template('sections/blog/_article.html')


class WrittenFile(TypedDict):
    """TypedDict representing a written file."""

    path: Path
    contents: str


def create_dir_if_not_exists(path: Path) -> Path:
    """Create a directory if it doesn't exist."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


def string_to_file(
    base_path: Path,
    file_location: str,
    contents: str,
) -> WrittenFile:
    """Create a file with the contents string.

    Args:
        base_path (str): The base path to write the file to.
        file_location (str): The location of the file to write (relative to the base path, including extension).
        contents (str): The contents to dump into the file.
    """
    fl = file_location.removeprefix('/')
    full_path = base_path / fl
    create_dir_if_not_exists(full_path.parent)  # Create directory for the file
    with open(full_path, 'w') as f:
        f.write(contents)

    return WrittenFile(path=base_path / fl, contents=contents)


def _render(
    base_path: Path,
    env: Environment,
    template: InternalTemplate,
    data: Any,
    additional_data: Any = {},
) -> WrittenFile:
    """Render the template.

    Args:
        base_path (Path): The base path to write the file to.
        env (Environment): The Jinja2 environment.
        template (InternalTemplate): The template to render.
        data (Any): The data to render the template with.
    """
    return string_to_file(
        base_path=base_path,
        file_location=f'{template.destination}',
        contents=get_template_function(template.template, env).render(
            data,
            **additional_data,
        ),
    )


def _render_homepage(
    base_path: Path,
    env: Environment,
    view: ViewModelHomePage,
) -> None:
    """Render the homepage.

    Args:
    base_path (Path): The base path to write the file to.
    env (Environment): The Jinja2 environment.
    view (ViewModelHomePage): The homepage view to generate.
    """
    _ = _render(
        base_path=base_path,
        env=env,
        template=view.targets.complete,
        data=view,
    )

    _ = _render(
        base_path=base_path,
        env=env,
        template=view.targets.hx,
        data=view,
    )


def _render_blog(
    base_path: Path,
    env: Environment,
    view: ViewModelBlog,
) -> None:
    """Render the blog index.

    Args:
        base_path (Path): The base path to write the file to.
        env (Environment): The Jinja2 environment.
        view (ViewModelWebsite): The Blog view to generate.
    """

    @curry_flip(1)
    def _for_each_post(
        post_view: ViewModelBlogPost,
        navigation: ViewModelNavigationMenu,
    ) -> None:
        _ = _render(
            base_path=base_path,
            env=env,
            template=post_view.targets.complete,
            data=post_view,
            additional_data={'navigation': navigation},
        )
        _ = _render(
            base_path=base_path,
            env=env,
            template=post_view.targets.hx,
            data=post_view,
        )

    _ = _render(
        base_path=base_path,
        env=env,
        template=view.targets.complete,
        data=view,
    )

    _ = _render(
        base_path=base_path,
        env=env,
        template=view.targets.hx,
        data=view,
    )

    _ = list(map(_for_each_post(navigation=view.navigation), view.posts))


def generate(
    base_path: Path,
    env: Environment,
    website: ViewModelWebsite,
) -> None:
    """Generate the website files.

    Args:
        website (ViewModelWebsite): The website to generate.
    """
    _render_homepage(base_path, env, website.homepage)
    _render_blog(base_path, env, website.blog)
