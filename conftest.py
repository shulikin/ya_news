from datetime import timedelta

import pytest

from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def new():
    new = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return new


@pytest.fixture
def news_list():
    for index in range(NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News.objects.create(
            title=f'Заголовок {index}',
            text='Текст.'
        )
        news.save()
    return index


@pytest.fixture
def comment(new, author):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Комментарий',
    )
    return comment


@pytest.fixture
def comments(author, new):
    now = timezone.now()
    comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=new,
            author=author,
            text=f"Текст {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def id_for_args(new):
    return new.id,


@pytest.fixture
def id_comment_for_args(comment):
    return comment.id,


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}
