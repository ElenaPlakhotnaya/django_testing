from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests import common


class TestNoteCreation(common.BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data_no_slug = {'text': cls.TEXT,
                                 'author': cls.user,
                                 'title': cls.TITLE}

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_start = Note.objects.count()
        self.client.post(self.ADD_NOTE, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.auth_client.post(self.ADD_NOTE, data=self.form_data)
        self.assertRedirects(response, self.DONE_NOTE)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.title, self.TITLE)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        Note.objects.all().delete()
        response = self.auth_client.post(
            self.ADD_NOTE, data=self.form_data_no_slug)
        self.assertRedirects(response, self.DONE_NOTE)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(note.title))


class TestNoteEditDelete(common.BaseTest):

    NEXT_TITLE = 'Заголовок второй'
    NEXT_TEXT = 'Заметка вторая'
    NEXT_SLUG = 'n'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {'text': cls.NEXT_TEXT,
                         'slug': cls.NEXT_SLUG,
                         'author': cls.author,
                         'title': cls.NEXT_TITLE}

    def test_author_can_delete_note(self):
        """Пользователь может удалить свои заметки."""
        response = self.author_client.delete(self.DELETE_NOTE)
        self.assertRedirects(response, self.DONE_NOTE)
        self.assertFalse(Note.objects.filter(author=self.author).exists())

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        notes_count_start = Note.objects.count()
        response = self.reader_client.delete(self.DELETE_NOTE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        Note.objects.filter(author=self.user).delete()
        response = self.author_client.post(self.EDIT_NOTE, data=self.form_data)
        self.assertRedirects(response, self.DONE_NOTE)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEXT_TEXT)
        self.assertEqual(self.note.slug, self.NEXT_SLUG)
        self.assertEqual(self.note.title, self.NEXT_TITLE)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может может редактировать чужие заметки."""
        response = self.reader_client.post(self.EDIT_NOTE, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)
        self.assertEqual(self.note.title, self.TITLE)


class TestSlugUnic(common.BaseTest):

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        notes_count_start = Note.objects.count()
        response = self.auth_client.post(self.ADD_NOTE, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_start)
