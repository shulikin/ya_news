from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
unnamed = lf('client')
author = lf('author_client')
reader = lf('reader_client')


@pytest.mark.parametrize(
    'url, argument_client, expected_status',
    [(lf('home_url'), unnamed, OK),
     (lf('detail_url'), unnamed, OK),
     (lf('login_url'), unnamed, OK),
     (lf('logout_url'), unnamed, OK),
     (lf('signup_url'), unnamed, OK),
     (lf('edit_url'), author, OK),
     (lf('delete_url'), author, OK),
     (lf('edit_url'), reader, NOT_FOUND),
     (lf('delete_url'), reader, NOT_FOUND),
     ],
)
def test_pages_availability_for_anonymous_user(
        url, argument_client, expected_status):
    response = argument_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('edit_url'),
     pytest.lazy_fixture('delete_url'),
     ),
)
def test_redirects(client, url, login_url):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
