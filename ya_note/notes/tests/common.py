from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Заметка'
    SLUG = 'm'
    SLUG_USER = 'n'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.user = User.objects.create(username='Гость')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.note_user = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG_USER,
            author=cls.user
        )
        cls.form_data = {'text': cls.TEXT,
                         'slug': cls.SLUG,
                         'author': cls.user,
                         'title': cls.TITLE}

    def setUp(self):
        self.HOME_PAGE = reverse('notes:home')
        self.ADD_NOTE = reverse('notes:add', None)
        self.LIST_NOTE = reverse('notes:list', None)
        self.DONE_NOTE = reverse('notes:success', None)
        self.EDIT_NOTE = reverse('notes:edit', args=(self.note.slug,))
        self.EDIT_NOTE_USER = reverse(
            'notes:edit', args=(self.note_user.slug,))
        self.DETAIL_NOTE = reverse('notes:detail', args=(self.note.slug,))
        self.DELETE_NOTE = reverse('notes:delete', args=(self.note.slug,))
        self.LOGIN = reverse('users:login', None)
        self.LOGOUT = reverse('users:logout', None)
        self.SIGNUP = reverse('users:signup', None)

        self.URLS = (self.HOME_PAGE,
                     self.ADD_NOTE,
                     self.LIST_NOTE,
                     self.DONE_NOTE,
                     self.EDIT_NOTE,
                     self.EDIT_NOTE,
                     self.DETAIL_NOTE,
                     self.DELETE_NOTE,
                     self.LOGIN,
                     self.LOGOUT,
                     self.SIGNUP)
        self.URLS_FOR_ANONYMOUS_USER = (self.HOME_PAGE,
                                        self.LOGIN,
                                        self.LOGOUT,
                                        self.SIGNUP)
        self.URLS_NOT_FOR_READER = (self.DETAIL_NOTE,
                                    self.EDIT_NOTE,
                                    self.DELETE_NOTE)
        self.URLS_FOR_REDIRECT = (self.LIST_NOTE,
                                  self.DONE_NOTE,
                                  self.ADD_NOTE,
                                  self.DETAIL_NOTE,
                                  self.EDIT_NOTE,
                                  self.DELETE_NOTE,)
