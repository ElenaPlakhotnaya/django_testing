from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

ANONYMOUS_CLIENT = pytest.lazy_fixture('anonym_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
HOME_PAGE_URL = pytest.lazy_fixture('home_page_url')
DETAL_NEWS_URL = pytest.lazy_fixture('detail_news_url')
DELETE_COMMENT_URL = pytest.lazy_fixture('delete_comment_url')
EDIT_COMMENT_URL = pytest.lazy_fixture('edit_comment_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
ANONYMOUS_URLS = (HOME_PAGE_URL, DETAL_NEWS_URL,
                  LOGIN_URL, LOGOUT_URL, SIGNUP_URL)
AUTHOR_URLS = (DELETE_COMMENT_URL, EDIT_COMMENT_URL)


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status', [
        (HOME_PAGE_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (DETAL_NEWS_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (DELETE_COMMENT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_COMMENT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
    ]
)
def test_pages_availability_for_different_user(url,
                                               parametrized_client,
                                               expected_status):
    """Страницы доступны разным пользователям."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    [DELETE_COMMENT_URL, EDIT_COMMENT_URL],
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """
    При попытке перейти на страницу
    редактирования или удаления комментария
    анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
