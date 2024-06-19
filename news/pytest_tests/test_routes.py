import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
comment_lazy = pytest.lazy_fixture('comment')
reader_lazy =pytest.lazy_fixture('reader_client')
author_lazy =pytest.lazy_fixture('author_client')
clause_lazy =pytest.lazy_fixture('clause')

@pytest.mark.parametrize(
    'name, user, status, args',
    (
        ('news:home', None, OK, None),
        ('news:detail', None, OK, clause_lazy),
        ('users:login', None, OK, None),
        ('users:logout', None, OK, None),
        ('users:signup', None, OK, None),
        ('news:edit', reader_lazy, NOT_FOUND, comment_lazy),
        ('news:delete', reader_lazy, NOT_FOUND, comment_lazy),
        ('news:edit', author_lazy, OK, comment_lazy),
        ('news:delete', author_lazy, OK, comment_lazy),
    )
)
def test_home_availability_for_users(client, user, name, status, args):
    if args is not None:
        url = reverse(name, args=(args.id,))
    else:
        url = reverse(name)
    if user is not None:
        response = user.get(url)
    else:
        response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name, comment_lazy',
    (
        ('news:edit', comment_lazy),
        ('news:delete', comment_lazy),
    )
)
def test_redirects(client, name, comment_lazy, login_url):
    url = reverse(name, args=(comment_lazy.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
