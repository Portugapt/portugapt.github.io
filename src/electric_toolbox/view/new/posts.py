"""Posts view."""

from pathlib import Path
from typing import Callable, List, TypedDict

from expression import Error, Nothing, Ok, Option, Result, Some
from expression.collections import Block, Map
from jinja2 import Environment, Template

from electric_toolbox.common.to_file import WrittenFile, create_dir_if_not_exists, string_to_file
from electric_toolbox.unfold.types.post import Post
from electric_toolbox.unfold.types.website import WebsiteMatadata
from electric_toolbox.view.new.types import Head


# Type aliases
class PostsIndexData(TypedDict):
    """TypedDict representing the index page data."""

    head: Head
    posts: List[Post]
    footer: str


class PostData(TypedDict):
    """TypedDict representing the data needed for rendering a single post."""

    head: Head
    post: Post
    footer: str  # Customize as needed


PostTemplate = Template
FileName = str


class TemplatedData(TypedDict):
    """TypedDict representing the templated data."""

    file_name: str
    in_folder: bool
    function: Callable[[Environment], Template]


class PostTemplateData(TypedDict):
    """TypedDict representing the template data for a single post."""

    file_name_selector: Callable[[], str]
    function: Callable[[Environment], PostTemplate]
    content_selector: Callable[[Post], str]


POSTS_INDEX_TEMPLATE: Map[str, TemplatedData] = Map.of_seq(
    [
        (
            'index_complete',
            TemplatedData(
                file_name='posts.html',
                in_folder=False,
                function=lambda env: env.get_template('blocks/posts_index.html'),
            ),
        ),
        (
            'hx-index',
            TemplatedData(
                file_name='hx_index.html',
                in_folder=True,
                function=lambda env: env.get_template('blocks/posts/list_posts.html'),
            ),
        ),
    ]
)


def base_create_file_name_selector(
    file_name: str,
    path: Path,
    post: Post,
) -> str:
    """Creates a function that selects the file name for a given post.

    Args:
        file_name_selector (Callable[[Path, Post], str]): A function that selects the file name for a given post.

    Returns:
        Callable[[Post], str]: A function that selects the file name for a given post.
    """
    create_dir_if_not_exists(path / post.slug)

    return file_name


POSTS_TEMPLATE: Map[str, PostTemplateData] = Map.of_seq(
    [
        (
            'post',
            PostTemplateData(
                file_name_selector=lambda: 'index.html',
                function=lambda env: env.get_template('blocks/posts/post/post.html'),
                content_selector=lambda post: post.contents,
            ),
        ),
        (
            'hx',
            PostTemplateData(
                file_name_selector=lambda: 'hx.html',
                function=lambda env: env.get_template('blocks/posts/post/hx_post.html'),
                content_selector=lambda post: post.contents,
            ),
        ),
        (
            'llm',
            PostTemplateData(
                file_name_selector=lambda: 'llm.json',
                function=lambda env: env.get_template('blocks/posts/post/llm.json'),
                content_selector=lambda post: post.model_dump_json(indent=2),
            ),
        ),
    ]
)


def metadata_to_page(
    metadata: WebsiteMatadata,
    posts: Block[Post],
) -> Result[PostsIndexData, Exception]:
    """Converts website metadata to page data.

    Args:
        metadata: The website metadata containing post information.
        posts: The list of posts to be displayed on the index page.

    Returns:
        A dictionary containing the data to be used in the index page template.
    """
    try:
        return Ok(
            {
                'head': {'title': metadata.title},
                'posts': list(posts),
                'footer': 'nothing',
            }
        )
    except Exception as e:
        return Error(e)


def metadata_to_post_view(
    metadata: WebsiteMatadata,
    post: Post,
) -> Result[PostData, Exception]:
    """Converts website metadata and a Post object to a dictionary for template rendering.

    Args:
        metadata: The website metadata.
        post: The Post object.

    Returns:
        Result[PostData, Exception]: Ok(PostData) if successful, Error(Exception) otherwise.
    """
    try:
        return Ok(
            {
                'head': {'title': f'{post.front_matter.title} | {metadata.title}'},
                'post': post,
                'footer': 'nothing',
            }
        )
    except Exception as e:
        return Error(e)


def generate_posts_index(
    metadata: WebsiteMatadata,
    j2_env: Environment,
    root_path: Path,
    folder: str = 'posts',
    write_to_file: bool = True,
) -> Result[Option[Map[str, WrittenFile]], Exception]:
    """Generates HTML files for blog posts.

    Args:
        metadata: The website metadata containing post information.
        j2_env: The Jinja2 environment for rendering templates.
        root_path: The root directory where the posts folder will be created/accessed.
        folder: The name of the folder to store the generated post HTML files. Defaults to 'posts'.
        write_to_file (bool): Whether to write the generated HTML to files. Defaults to True.

    """
    create_dir_if_not_exists(root_path / folder)
    return (
        metadata_to_page(metadata=metadata, posts=metadata.posts).map(
            lambda data: Some(
                POSTS_INDEX_TEMPLATE.map(
                    lambda _, templated_data: string_to_file(
                        path=root_path / folder if templated_data['in_folder'] else root_path,
                        file_name=templated_data['file_name'],
                        contents=templated_data['function'](j2_env).render(data),
                    )
                )
            )
        )
        if write_to_file
        else Ok(Nothing)
    )


def generate_post(
    metadata: WebsiteMatadata,
    post: Post,
    template_data: PostTemplateData,
    j2_env: Environment,
    post_path: Path,
) -> Result[WrittenFile, Exception]:
    """Generates a single post file based on the given template and data.

    Args:
        metadata: The website metadata.
        post: The Post object to render.
        template_data: The template data, including the template function, content selector, and file name selector.
        j2_env: The Jinja2 environment.
        root_path: The root path for the website.
        folder: The subfolder for posts (default: "posts").

    Returns:
        Result[WrittenFile, Exception]: Ok(WrittenFile) if successful, Error(Exception) otherwise.
    """
    return metadata_to_post_view(metadata, post).map(
        lambda data: string_to_file(
            path=post_path,
            file_name=template_data['file_name_selector'](),
            contents=template_data['function'](j2_env).render(data, content=template_data['content_selector'](post)),
        )
    )


def all_post_types_generator(
    metadata: WebsiteMatadata,
    j2_env: Environment,
    path: Path,
    post: Post,
) -> Map[str, Result[WrittenFile, Exception]]:
    """Generates HTML files for blog posts.

    Args:
        metadata (WebsiteMatadata): The website metadata containing post information.
        j2_env (Environment): The Jinja2 environment for rendering templates.
        path (Path): The root directory where the posts folder will be created/accessed.
        post (Post): The Post object to render.

    Returns:
        Result[Option[Map[str, WrittenFile]], Exception]: Ok(Option[Map[str, WrittenFile]]) if successful, Error(Exception) otherwise.
    """
    post_path = create_dir_if_not_exists(path / post.slug)
    return POSTS_TEMPLATE.map(
        lambda _, templated_data: generate_post(metadata, post, templated_data, j2_env, post_path)
    )


def generate_posts(
    metadata: WebsiteMatadata,
    j2_env: Environment,
    root_path: Path,
    folder: str = 'posts',
    write_to_file: bool = True,
) -> Block[Map[str, Result[WrittenFile, Exception]]]:
    """Generates HTML files for blog posts.

    Args:
        metadata: The website metadata containing post information.
        j2_env: The Jinja2 environment for rendering templates.
        root_path: The root directory where the posts folder will be created/accessed.
        folder: The name of the folder to store the generated post HTML files. Defaults to 'posts'.
        write_to_file (bool): Whether to write the generated HTML to files. Defaults to True.

    Returns:
        Result[Option[Map[str, WrittenFile]], Exception]: Ok(Some(Map[str, WrittenFile])) if successful
                                                          and write_to_file is True,
                                                          Ok(Nothing) if successful and write_to_file is False,
                                                          Error(Exception) if an error occurs.
    """
    create_dir_if_not_exists(root_path / folder)

    return metadata.posts.map(
        lambda post: all_post_types_generator(metadata=metadata, j2_env=j2_env, path=root_path / folder, post=post)
    )


def generate_post_blocks(
    metadata: WebsiteMatadata,
    j2_env: Environment,
    root_path: Path,
    write_to_file: bool = True,
) -> None:
    """Generates the entire website, including the posts index and individual posts.

    Args:
        metadata: The website metadata.
        j2_env: The Jinja2 environment for rendering templates.
        root_path: The root directory where the website files will be generated.
        write_to_file: Whether to write the generated files to disk.

    Returns:
        Result[Option[Map[str, WrittenFile]], Exception]:
            - Ok(Some(Map[str, WrittenFile])) if successful and write_to_file is True,
            - Ok(Nothing) if successful and write_to_file is False,
            - Error(Exception) if an error occurs.
    """
    # Generate posts index

    generate_posts_index(metadata, j2_env, root_path, write_to_file=write_to_file)

    # Generate posts
    generate_posts(metadata, j2_env, root_path, write_to_file=write_to_file)
