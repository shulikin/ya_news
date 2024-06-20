import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('news')
def test_news_count(client, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('news')
def test_news_order(client, home_url):
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url, comments):
    response = client.get(detail_url)
    assert "news" in response.context
    comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_form_availability_for_different_users(
        reader_client, detail_url):
    response = reader_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
