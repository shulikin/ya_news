import pytest
from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count_and_order(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert 'news_list' in response.context
    news_count = len(object_list)
    assert news_count is NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comments, new):
    url = reverse("news:detail", args=(new.id,))
    response = client.get(url)
    assert "news" in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    sorted_comments = sorted(
        all_comments,
        key=lambda comment: comment.created,
        reverse=False
    )
    assert sorted_comments == comments


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_page',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_form_availability_for_different_users(
        new, parametrized_client, form_in_page
):
    url = reverse('news:detail', args=(new.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_page
