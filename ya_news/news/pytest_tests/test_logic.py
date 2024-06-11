from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}


def test_user_can_create_comment(author_client, author, detail_news_url,
                                 form_data):
    """Авторизованный пользователь может отправить комментарий."""
    assert Comment.objects.count() == 0
    url = detail_news_url
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_anonymous_user_cant_create_comment(client, detail_news_url, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    comments = Comment.objects.count()
    url = detail_news_url
    client.post(url, data=form_data)
    assert Comment.objects.count() == comments


def test_user_cant_use_bad_words(author_client, detail_news_url, form_data):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    comments = Comment.objects.count()
    url = detail_news_url
    form_data['text'] = BAD_WORDS[0]
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == comments


def test_author_can_edit_comment(author_client, form_data, comment, news,
                                 edit_comment_url, detail_news_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    assert Comment.objects.count() == 1
    url = edit_comment_url
    response = author_client.post(url, form_data)
    assertRedirects(response, detail_news_url + '#comments')
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client, comment,
                                                edit_comment_url, form_data):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = edit_comment_url
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_author_can_delete_comment(author_client, comment, detail_news_url,
                                   delete_comment_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = delete_comment_url
    response = author_client.post(url)
    assertRedirects(response, detail_news_url + '#comments')
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cant_delete_comment_of_another_user(not_author_client, comment,
                                                  delete_comment_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = delete_comment_url
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert Comment.objects.count() == 1
    assert comment.text == comment_from_db.text
