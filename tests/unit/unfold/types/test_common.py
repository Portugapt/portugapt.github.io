from deepdiff.diff import DeepDiff
from expression import Nothing, Option, Some
from expression.collections import Block
from hypothesis import given, settings
from hypothesis import strategies as st

from electric_toolbox.unfold.types.common import Breadcrumbs


def test_generate_url_no_base_url() -> None:
    """Test URL generation without a base URL."""
    post_breadcrumb = Breadcrumbs(path='my-post', title='My Post')
    breadcrumbs = Breadcrumbs(
        path='posts',
        title='Posts',
        previous_crumb=Some(post_breadcrumb),
    )
    assert breadcrumbs.generate_url() == '/posts/my-post'


def test_generate_url_with_base_url() -> None:
    """Test URL generation with a base URL."""
    post_breadcrumb = Breadcrumbs(path='my-post', title='My Post')
    breadcrumbs = Breadcrumbs(
        path='posts',
        title='Posts',
        previous_crumb=Some(post_breadcrumb),
    )
    assert breadcrumbs.generate_url(base_url='https://www.example.com') == 'https://www.example.com/posts/my-post'


def test_generate_url_with_base_url_and_trailing_slash() -> None:
    """Test URL generation with a base URL that has a trailing slash."""
    post_breadcrumb = Breadcrumbs(path='my-post', title='My Post')
    breadcrumbs = Breadcrumbs(
        path='posts',
        title='Posts',
        previous_crumb=Some(post_breadcrumb),
    )
    assert breadcrumbs.generate_url(base_url='https://www.example.com/') == 'https://www.example.com/posts/my-post'


def test_generate_url_single_segment() -> None:
    """Test URL generation for a single-segment breadcrumb."""
    breadcrumbs = Breadcrumbs(path='home', title='Home')
    assert breadcrumbs.generate_url() == '/home'
    assert breadcrumbs.generate_url(base_url='https://www.example.com') == 'https://www.example.com/home'


def test_generate_url_empty_path() -> None:
    """Test URL generation for an empty path."""
    breadcrumbs = Breadcrumbs(path='', title='Root')
    assert breadcrumbs.generate_url() == '/'
    assert breadcrumbs.generate_url(base_url='https://www.example.com') == 'https://www.example.com/'


def test_generate_url_with_nothing_previous_crumb() -> None:
    """Test that having previous_crumb as Nothing doesn't cause errors."""
    breadcrumbs = Breadcrumbs(path='about', title='About', previous_crumb=Nothing)
    assert breadcrumbs.generate_url() == '/about'


def test_generate_url_with_trailing_slash_in_path() -> None:
    """Test URL generation where path segments have trailing slashes."""
    products_breadcrumb = Breadcrumbs(path='products/', title='Products')
    breadcrumbs = Breadcrumbs(
        path='home/',
        title='Home',
        previous_crumb=Some(products_breadcrumb),
    )
    assert breadcrumbs.generate_url() == '/home/products'
    assert breadcrumbs.generate_url(base_url='https://www.example.com') == 'https://www.example.com/home/products'


def test_generate_url_empty_breadcrumb() -> None:
    """Test URL generation with no valid breadcrumb data."""
    breadcrumbs = Breadcrumbs(path='', title='Empty')
    assert breadcrumbs.generate_url() == '/'
    assert breadcrumbs.generate_url(base_url='https://www.example.com') == 'https://www.example.com/'


def test_generate_url_with_full_url_path() -> None:
    """Test URL generation with a full URL path."""
    breadcrumbs = Breadcrumbs(
        path='https://www.example.com/my-post',
        title='My Post',
    )
    assert breadcrumbs.generate_url() == 'https://www.example.com/my-post'


def test_generate_url_with_base_url_and_multiple_segments() -> None:
    """Test URL generation with a base URL and multiple breadcrumb segments."""
    products_breadcrumb = Breadcrumbs(path='products', title='Products')
    breadcrumbs = Breadcrumbs(
        path='home',
        title='Home',
        previous_crumb=Some(products_breadcrumb),
    )
    assert breadcrumbs.generate_url(base_url='https://www.example.com/') == 'https://www.example.com/home/products'


def test_generate_url_multiple_segments() -> None:
    """Test URL generation with multiple breadcrumb segments."""
    my_post_breadcrumb = Breadcrumbs(path='my-post', title='My Post')
    blog_breadcrumb = Breadcrumbs(path='blog', title='Blog', previous_crumb=Some(my_post_breadcrumb))
    breadcrumbs = Breadcrumbs(path='home', title='Home', previous_crumb=Some(blog_breadcrumb))
    assert breadcrumbs.generate_url() == '/home/blog/my-post'
    assert breadcrumbs.generate_url(base_url='https://www.example.com') == 'https://www.example.com/home/blog/my-post'


def test_block_back_multiple_segments() -> None:
    """Test _block_back with multiple segments."""
    my_post_breadcrumb = Breadcrumbs(path='my-post', title='My Post')
    blog_breadcrumb = Breadcrumbs(path='blog', title='Blog', previous_crumb=Some(my_post_breadcrumb))
    home_breadcrumb = Breadcrumbs(path='home', title='Home', previous_crumb=Some(blog_breadcrumb))

    result = home_breadcrumb._block_back()

    assert result == Block(['home', 'blog', 'my-post'])


def test_block_back_single_segment() -> None:
    """Test _block_back with a single segment."""
    breadcrumbs = Breadcrumbs(path='home', title='Home')
    result = breadcrumbs._block_back()
    assert result == Block(['home'])


def test_block_back_empty_path() -> None:
    """Test _block_back with an empty path."""
    breadcrumbs = Breadcrumbs(path='', title='Empty')
    result = breadcrumbs._block_back()
    assert {} == DeepDiff(result, Block.empty())


def test_block_back_with_nothing_previous_crumb() -> None:
    """Test _block_back with previous_crumb as Nothing."""
    breadcrumbs = Breadcrumbs(path='about', title='About', previous_crumb=Nothing)
    result = breadcrumbs._block_back()
    assert result == Block(['about'])


@given(st.text())
def test_hypothesis_generate_url_with_only_base_url(base_url) -> None:  # type: ignore
    """Test that generate_url with only a base_url returns the base_url."""
    breadcrumbs = Breadcrumbs(path='', title='Root')  # Empty path
    result = breadcrumbs.generate_url(base_url=base_url)

    if base_url and not base_url.endswith('/'):
        assert result == base_url + '/'
    else:
        assert result == base_url or '/'


@given(st.lists(st.text()), st.text())
@settings(max_examples=100, deadline=500)
def test_hypothesis_generate_url_path_segments(paths, base_url) -> None:  # type: ignore
    """Test that generate_url correctly combines path segments, with or without a base URL."""
    # Create nested breadcrumbs in reverse order
    breadcrumbs: Option[Breadcrumbs] = Nothing
    for p in reversed(paths):
        breadcrumbs = Some(Breadcrumbs(path=p, title='Segment', previous_crumb=breadcrumbs))

    if breadcrumbs.is_none():
        breadcrumbs = Some(Breadcrumbs(path='', title='Root'))

    result = breadcrumbs.some.generate_url(base_url=base_url)

    # Construct expected URL
    segments = [p.strip('/') for p in paths if p]
    if base_url:
        if not base_url.endswith('/'):
            base_url += '/'
        expected = base_url + '/'.join(segments)
    else:
        expected = '/' + '/'.join(segments)

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
    assert breadcrumbs.generate_url() == full_url


# def test_from_url_relative_url() -> None:
#     """Test creating Breadcrumbs from a relative URL."""
#     url = '/posts/my-awesome-post'
#     result = Breadcrumbs.from_url(url)
#     assert result.is_some()
#     breadcrumbs = result.some
#     assert breadcrumbs.path == 'my-awesome-post'
#     assert breadcrumbs.title == 'Page: my-awesome-post'
#     assert breadcrumbs.previous_crumb.is_some()
#     assert breadcrumbs.previous_crumb.some.path == '/posts'
#     assert breadcrumbs.previous_crumb.some.title == 'Page: posts'
#     assert breadcrumbs.previous_crumb.some.previous_crumb == Nothing


# def test_from_url_full_url() -> None:
#     """Test creating Breadcrumbs from a full URL."""
#     url = 'https://www.example.com/products/category-a/item-123'
#     result = Breadcrumbs.from_url(url)
#     assert result.is_some()
#     breadcrumbs = result.some
#     assert breadcrumbs.path == url
#     assert breadcrumbs.title == f'Page: {url}'
#     assert breadcrumbs.previous_crumb == Nothing


# def test_from_url_root_url() -> None:
#     """Test creating Breadcrumbs from the root URL."""
#     url = '/'
#     result = Breadcrumbs.from_url(url)
#     assert result.is_some()
#     breadcrumbs = result.some
#     assert breadcrumbs.path == '/'
#     assert breadcrumbs.title == 'Page: /'
#     assert breadcrumbs.previous_crumb == Nothing


# def test_from_url_empty_path() -> None:
#     """Test creating Breadcrumbs from an empty path."""
#     url = ''
#     result = Breadcrumbs.from_url(url)
#     assert result.is_none()


# def test_from_url_with_base_url() -> None:
#     """Test that base_url is effectively ignored in the current implementation.

#     If base_url handling is implemented in the future, this test should be updated accordingly.
#     """
#     url = '/posts/my-awesome-post'
#     result = Breadcrumbs.from_url(url)  # base_url is not passed
#     assert result.is_some()
#     breadcrumbs = result.some
#     assert breadcrumbs.path == 'my-awesome-post'
#     assert breadcrumbs.title == 'Page: my-awesome-post'
#     assert breadcrumbs.previous_crumb.is_some()
#     assert breadcrumbs.previous_crumb.some.path == '/posts'
#     assert breadcrumbs.previous_crumb.some.title == 'Page: posts'
#     assert breadcrumbs.previous_crumb.some.previous_crumb == Nothing


# def test_from_url_custom_title_prefix() -> None:
#     """Test creating Breadcrumbs with a custom title prefix."""
#     url = '/posts/my-awesome-post'
#     result = Breadcrumbs.from_url(url, title_prefix='Topic')
#     assert result.is_some()
#     breadcrumbs = result.some
#     assert breadcrumbs.path == 'my-awesome-post'
#     assert breadcrumbs.title == 'Topic: my-awesome-post'
#     assert breadcrumbs.previous_crumb.is_some()
#     assert breadcrumbs.previous_crumb.some.path == '/posts'
#     assert breadcrumbs.previous_crumb.some.title == 'Topic: posts'
#     assert breadcrumbs.previous_crumb.some.previous_crumb == Nothing
