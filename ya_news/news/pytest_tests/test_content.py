import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


def test_authorized_client_has_form(author_client, detail_news_url):
    """
    Авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости.
    """
    response = author_client.get(detail_news_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_anonymous_client_has_no_form(client, detail_news_url):
    """
    Анонимному пользователю недоступна форма
    для отправки комментария на странице отдельной новости.
    """
    response = client.get(detail_news_url)
    form = response.context.get('form')
    assert form is None


@pytest.mark.usefixtures('list_news')
def test_news_count(client, home_page_url):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_page_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('list_news')
def test_news_order(client, home_page_url):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_page_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('list_comments')
def test_comments_order(client, news, detail_news_url):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(detail_news_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
