# conftest.py
import pytest
from django.utils import timezone
# Импортируем класс клиента.
from django.test.client import Client
from datetime import datetime, timedelta
# Импортируем модель заметки, чтобы создать экземпляр.
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
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Новость',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}


@pytest.fixture
def list_news():
    today = datetime.today()
    list_news = []
    for index in range(NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News.objects.create(
            title='Новость {index}',
            text='Текст новости',
        )
        news.date = today - timedelta(days=index)
        news.save()
        list_news.append(news)
    return list_news


@pytest.fixture
def list_comments(news, author):
    now = timezone.now()
    list_comment = []
    for index in range(2):
        comment = Comment.objects.create(
            text='Текст {index}',
            news=news,
            author=author,
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        list_comment.append(comment)
