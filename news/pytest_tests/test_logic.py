from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_create_comment(client, form_data, id_for_args):
    url = reverse('news:detail', args=id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_create_comment(author_client, author, id_for_args, form_data):
    url = reverse('news:detail', args=id_for_args)
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_bad_words(admin_client, id_for_args):
    url = reverse('news:detail', args=id_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_edit_comment(author_client, comment, form_data, id_for_args,
                             id_comment_for_args):
    url = reverse('news:detail', args=id_for_args)
    url_to_comments = f'{url}#comments'
    edit_url = reverse('news:edit', args=id_comment_for_args)
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_delete_comment(author_client, id_for_args,
                               id_comment_for_args):
    url = reverse('news:detail', args=id_for_args)
    url_to_comments = f'{url}#comments'
    delete_url = reverse('news:delete', args=id_comment_for_args)
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_another_user_edit_comment(admin_client, form_data, comment,
                                   id_comment_for_args):
    url = reverse('news:edit', args=id_comment_for_args)
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_another_user_delete_comment(admin_client, comment,
                                     id_comment_for_args):
    url = reverse('news:delete', args=id_comment_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
