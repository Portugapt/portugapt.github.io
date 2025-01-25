"""Test internal functions of the breadcrumbs component."""

from deepdiff.diff import DeepDiff
from expression import Nothing, Option, Some
from expression.collections import Block
from hypothesis import given, settings
from hypothesis import strategies as st

from electric_toolbox.constants import ExistingTemplates
from electric_toolbox.parsing import TargetFiles, Template
from electric_toolbox.parsing.components.breadcrumbs import Breadcrumbs, block_of_paths, generate_url


def test_generate_url_no_base_url() -> None:
    """Test URL generation without a base URL."""
    home_crumb = Breadcrumbs(
        path='/',
        title='Home',
        targets=TargetFiles(
            complete=Template(destination='', template=ExistingTemplates.INDEX, extension=''),
            hx=Template(destination='', template=ExistingTemplates.INDEX_HX, extension=''),
        ),
    )
    previous_crumb = Breadcrumbs(
        path='posts',
        title='Posts',
        targets=TargetFiles(
            complete=Template(destination='posts', template=ExistingTemplates.BLOG_INDEX, extension='html'),
            hx=Template(destination='posts_hx', template=ExistingTemplates.BLOG_INDEX_HX, extension='html'),
        ),
        previous_crumb=Some(home_crumb),
    )
    post_breadcrumb = Breadcrumbs(
        path='my-post',
        title='My Post',
        targets=TargetFiles(
            complete=Template(destination='my-post', template=ExistingTemplates.BLOG_ARTICLE, extension='html'),
            hx=Template(destination='my-post_hx', template=ExistingTemplates.BLOG_ARTICLE_HX, extension='html'),
        ),
        previous_crumb=Some(previous_crumb),
    )
    assert generate_url(crumb=post_breadcrumb) == '/posts/my-post.html'


def test_generate_url_with_base_url() -> None:
    """Test URL generation with a base URL."""
    prev_breadcrumbs = Breadcrumbs(
        path='posts',
        title='Posts',
        targets=TargetFiles(
            complete=Template(destination='posts', template=ExistingTemplates.BLOG_INDEX, extension='html'),
            hx=Template(destination='posts_hx', template=ExistingTemplates.BLOG_INDEX_HX, extension='html'),
        ),
    )
    post_breadcrumb = Breadcrumbs(
        path='my-post',
        title='My Post',
        targets=TargetFiles(
            complete=Template(destination='my-post', template=ExistingTemplates.BLOG_ARTICLE, extension='html'),
            hx=Template(destination='my-post_hx', template=ExistingTemplates.BLOG_ARTICLE_HX, extension='html'),
        ),
        previous_crumb=Some(prev_breadcrumbs),
    )
    assert (
        generate_url(crumb=post_breadcrumb, base_url='https://www.example.com')
        == 'https://www.example.com/posts/my-post.html'
    )


def test_generate_url_with_base_url_and_trailing_slash() -> None:
    """Test URL generation with a base URL that has a trailing slash."""
    prev_breadcrumbs = Breadcrumbs(
        path='posts',
        title='Posts',
        targets=TargetFiles(
            complete=Template(destination='posts', template=ExistingTemplates.BLOG_INDEX, extension='html'),
            hx=Template(destination='posts_hx', template=ExistingTemplates.BLOG_INDEX_HX, extension='html'),
        ),
    )
    post_breadcrumb = Breadcrumbs(
        path='my-post',
        title='My Post',
        targets=TargetFiles(
            complete=Template(destination='my-post', template=ExistingTemplates.BLOG_ARTICLE, extension='html'),
            hx=Template(destination='my-post_hx', template=ExistingTemplates.BLOG_ARTICLE_HX, extension='html'),
        ),
        previous_crumb=Some(prev_breadcrumbs),
    )
    assert (
        generate_url(crumb=post_breadcrumb, base_url='https://www.example.com/')
        == 'https://www.example.com/posts/my-post.html'
    )


def test_generate_url_single_segment() -> None:
    """Test URL generation for a single-segment breadcrumb."""
    breadcrumbs = Breadcrumbs(
        path='TODELETE',
        targets=TargetFiles(
            complete=Template(destination='index', template=ExistingTemplates.INDEX, extension='.html'),
            hx=Template(destination='', template=ExistingTemplates.INDEX_HX, extension=''),
        ),
        title='Home',
    )
    assert generate_url(crumb=breadcrumbs) == '/index'
    assert generate_url(crumb=breadcrumbs, base_url='https://www.example.com') == 'https://www.example.com/index.html'


def test_generate_url_empty_path() -> None:
    """Test URL generation for an empty path."""
    breadcrumbs = Breadcrumbs(
        path='',
        title='Root',
        targets=TargetFiles(
            complete=Template(destination='index', template=ExistingTemplates.INDEX, extension='.html'),
            hx=Template(destination='', template=ExistingTemplates.INDEX_HX, extension=''),
        ),
    )
    assert generate_url(crumb=breadcrumbs) == '/'
    assert generate_url(crumb=breadcrumbs, base_url='https://www.example.com') == 'https://www.example.com'


def test_generate_url_with_nothing_previous_crumb() -> None:
    """Test that having previous_crumb as Nothing doesn't cause errors."""
    breadcrumbs = Breadcrumbs(path='about', title='About', previous_crumb=Nothing)
    assert generate_url(crumb=breadcrumbs) == '/about'


def test_generate_url_with_trailing_slash_in_path() -> None:
    """Test URL generation where path segments have trailing slashes."""
    breadcrumbs = Breadcrumbs(
        path='home/',
        title='Home',
    )
    products_breadcrumb = Breadcrumbs(path='products/', title='Products', previous_crumb=Some(breadcrumbs))
    assert generate_url(crumb=products_breadcrumb) == '/home/products'
    assert (
        generate_url(crumb=products_breadcrumb, base_url='https://www.example.com')
        == 'https://www.example.com/home/products'
    )


def test_generate_url_empty_breadcrumb() -> None:
    """Test URL generation with no valid breadcrumb data."""
    breadcrumbs = Breadcrumbs(path='', title='Empty')
    assert generate_url(crumb=breadcrumbs) == '/'
    assert generate_url(crumb=breadcrumbs, base_url='https://www.example.com') == 'https://www.example.com'


def test_generate_url_with_full_url_path() -> None:
    """Test URL generation with a full URL path."""
    breadcrumbs = Breadcrumbs(
        path='https://www.example.com/my-post',
        title='My Post',
    )
    assert generate_url(crumb=breadcrumbs) == 'https://www.example.com/my-post'


def test_generate_url_with_base_url_and_multiple_segments() -> None:
    """Test URL generation with a base URL and multiple breadcrumb segments."""
    breadcrumbs = Breadcrumbs(
        path='home',
        title='Home',
    )
    products_breadcrumb = Breadcrumbs(path='products', title='Products', previous_crumb=Some(breadcrumbs))
    assert (
        generate_url(crumb=products_breadcrumb, base_url='https://www.example.com/')
        == 'https://www.example.com/home/products'
    )


def test_generate_url_multiple_segments() -> None:
    """Test URL generation with multiple breadcrumb segments."""
    breadcrumbs = Breadcrumbs(path='home', title='Home')
    blog_breadcrumb = Breadcrumbs(path='blog', title='Blog', previous_crumb=Some(breadcrumbs))
    my_post_breadcrumb = Breadcrumbs(path='my-post', title='My Post', previous_crumb=Some(blog_breadcrumb))
    assert generate_url(crumb=my_post_breadcrumb) == '/home/blog/my-post'
    assert (
        generate_url(crumb=my_post_breadcrumb, base_url='https://www.example.com')
        == 'https://www.example.com/home/blog/my-post'
    )


@given(st.text())
def test_hypothesis_generate_url_with_only_base_url(base_url) -> None:  # type: ignore
    """Test that generate_url with only a base_url returns the base_url."""
    breadcrumbs = Breadcrumbs(path='', title='Root')  # Empty path
    result = generate_url(crumb=breadcrumbs, base_url=base_url)

    assert result == base_url if base_url else '/'


@given(st.lists(st.text()), st.text())
@settings(max_examples=100, deadline=500)
def test_hypothesis_generate_url_path_segments(paths, base_url) -> None:  # type: ignore
    """Test that generate_url correctly combines path segments, with or without a base URL."""
    # Create nested breadcrumbs in reverse order
    breadcrumbs: Option[Breadcrumbs] = Nothing
    for p in paths:
        breadcrumbs = Some(Breadcrumbs(path=p, title='Segment', previous_crumb=breadcrumbs))

    if breadcrumbs.is_none():
        breadcrumbs = Some(Breadcrumbs(path='', title='Root'))

    result = generate_url(crumb=breadcrumbs.some, base_url=base_url)

    # Construct expected URL (Approach 3: No trailing slashes unless base_url has one)
    segments = [p.strip('/') for p in paths if p.strip('/')]  # Filter out segments that are only slashes

    if base_url:
        if base_url.endswith('/'):
            expected = base_url + '/'.join(segments)
        else:
            # Only add '/' if there are segments
            expected = base_url + ('/' + '/'.join(segments) if segments else '')
    else:
        expected = '/' + '/'.join(segments) if segments else '/'

    assert result == expected


@given(
    st.sampled_from(['http://', 'https://']),
    st.just('www.'),
    st.text(min_size=3),
    st.sampled_from(['.com', '.org', '.net']),
    st.lists(st.text(min_size=1)),
)
@settings(max_examples=50)
def test_hypothesis_generate_url_with_full_url_path(protocol, subdomain, domain, tld, path_segments) -> None:  # type: ignore
    """Test that generate_url returns the full URL if the first path segment is a full URL."""
    full_url = f'{protocol}{subdomain}{domain}{tld}'

    if path_segments:
        full_url += '/' + '/'.join(path_segments)

    breadcrumbs = Breadcrumbs(path=full_url, title='Full URL')
    assert generate_url(crumb=breadcrumbs) == full_url


def test_block_of_paths_multiple_segments() -> None:
    """Test block_of_paths with multiple segments."""
    home_breadcrumb = Breadcrumbs(path='home', title='Home')
    blog_breadcrumb = Breadcrumbs(path='blog', title='Blog', previous_crumb=Some(home_breadcrumb))
    my_post_breadcrumb = Breadcrumbs(path='my-post', title='My Post', previous_crumb=Some(blog_breadcrumb))

    result = block_of_paths(crumb=my_post_breadcrumb)

    assert result == Block(['home', 'blog', 'my-post'])


def test_block_of_paths_single_segment() -> None:
    """Test block_of_paths with a single segment."""
    breadcrumbs = Breadcrumbs(path='home', title='Home')
    result = block_of_paths(crumb=breadcrumbs)
    assert result == Block(['home'])


def test_block_of_paths_empty_path() -> None:
    """Test block_of_paths with an empty path."""
    breadcrumbs = Breadcrumbs(path='', title='Empty')
    result = block_of_paths(crumb=breadcrumbs)
    assert {} == DeepDiff(result, Block.empty())


def test_block_of_paths_with_nothing_previous_crumb() -> None:
    """Test block_of_paths with previous_crumb as Nothing."""
    breadcrumbs = Breadcrumbs(path='about', title='About', previous_crumb=Nothing)
    result = block_of_paths(crumb=breadcrumbs)
    assert result == Block(['about'])
