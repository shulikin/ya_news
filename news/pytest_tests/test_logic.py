from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_create_comment(client, detail_url, form_data):
    comments_count = Comment.objects.count()
    client.post(detail_url, data=form_data)
    assert comments_count == Comment.objects.count()


def test_user_create_comment(
    author_client, author, detail_url, form_data, clause
):
    Comment.objects.all().delete()
    response = author_client.post(detail_url, data=form_data)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == clause


@pytest.mark.django_db
def test_bad_words(author_client, detail_url):
    comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert comments_count == Comment.objects.count()
    form = response.context_data['form']
    assert form.errors == {'text': [WARNING]}


def test_author_edit_comment(
    author_client, comment, form_data, edit_url, detail_url, author, clause
):
    url_to_comments = f'{detail_url}#comments'
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == clause


def test_author_delete_comment(
    author_client, delete_url, detail_url
):
    url_to_comments = f'{detail_url}#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_another_user_edit_comment(admin_client, form_data, comment,
                                   edit_url):
    response = admin_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_another_user_delete_comment(admin_client, delete_url):
    response = admin_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
