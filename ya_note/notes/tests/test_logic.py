from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    TITLE = 'Заголовок'
    TEXT = 'Заметка'
    SLUG = 'm'

    @classmethod
    def setUpTestData(cls):

        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Гость')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.TEXT,
                         'slug': cls.SLUG,
                         'author': cls.user,
                         'title': cls.TITLE}
        cls.form_data_no_slug = {'text': cls.TEXT,
                                 'author': cls.user,
                                 'title': cls.TITLE}

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.title, self.TITLE)
        # self.assertEqual(note.author, self.user)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        response = self.auth_client.post(self.url, data=self.form_data_no_slug)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(note.title))


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Заметка'
    SLUG = 'm'
    NEXT_TITLE = 'Заголовок второй'
    NEXT_TEXT = 'Заметка вторая'
    NEXT_SLUG = 'n'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT, slug=cls.SLUG, author=cls.author)
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'text': cls.NEXT_TEXT,
                         'slug': cls.NEXT_SLUG,
                         'author': cls.author,
                         'title': cls.NEXT_TITLE}

    def test_author_can_delete_note(self):
        """Пользователь может удалить свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEXT_TEXT)
        self.assertEqual(self.note.slug, self.NEXT_SLUG)
        self.assertEqual(self.note.title, self.NEXT_TITLE)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может может редактировать чужие заметки."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)
        self.assertEqual(self.note.title, self.TITLE)


class TestSlugUnic(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Заметка'
    SLUG = 'm'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Гость')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT, author=cls.user, slug=cls.SLUG)
        cls.form_data = {'text': cls.TEXT,
                         'slug': cls.SLUG,
                         'author': cls.user,
                         'title': cls.TITLE}

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
