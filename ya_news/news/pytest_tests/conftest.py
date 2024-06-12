from datetime import datetime, timedelta

from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

import pytest

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def anonym(django_user_model):
    return django_user_model.objects.create(username='Аноним')


@pytest.fixture
def anonym_client():
    client = Client()
    return client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Новость',
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )


@pytest.fixture
def list_news():
    today = datetime.today()
    list_news = []
    for index in range(NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        list_news.append(news)
    News.objects.bulk_create(list_news)


@pytest.fixture
def list_comments(news, author):
    for index in range(10):
        comment = Comment.objects.create(
            text=f'Текст {index}',
            news=news,
            author=author,
        )
        comment.save()


@pytest.fixture
def home_page_url():
    return reverse('news:home')


@pytest.fixture
def detail_news_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def login_url():
    return reverse('users:login', None)


@pytest.fixture
def logout_url():
    return reverse('users:logout', None)


@pytest.fixture
def signup_url():
    return reverse('users:signup', None)
