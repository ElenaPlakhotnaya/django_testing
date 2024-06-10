from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesListPage(TestCase):

    NOTES_LIST = reverse('notes:list')
    TITLE = 'Заголовок'
    TEXT = 'Заметка'
    SLUG = 'm'

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create(username='Гость')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')

        cls.note = Note.objects.create(
            title=cls.TITLE, text=cls.TEXT, author=cls.user, slug=cls.SLUG)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_in_list_for_author(self):
        """
        Jтдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        response = self.client.get(self.NOTES_LIST)
        if response.context is not None:
            object_list = response.context['object_list']
            list_count = object_list.count()
            notes_count = Note.objects.count()
            self.assertEqual(list_count, notes_count)

    def test_create_note_page_contains_form(self):
        """на страницы создания передаются формы."""
        response = self.auth_client.get(self.url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_contains_form(self):
        """
        На страницы редактирования передаются формы.
        """
        response = self.auth_client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestAuthorNotesListPage(TestCase):

    NOTES_LIST = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        Note.objects.bulk_create(
            Note(title=f'Заметка {index}', text='Просто текст.',
                 author=cls.author, slug=f'{index}')
            for index in range(1, 7)
        )
        Note.objects.create(
            title='Заметка', text='Просто текст.', author=cls.reader, slug='m'
        )

    def test_note_not_in_list_for_another_user(self):
        """
        В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        response = self.author_client.get(self.NOTES_LIST)
        if response.context is not None:
            object_list = response.context['object_list']
            list_count = object_list.count()
            notes_count = Note.objects.filter(author=self.author).count()
            self.assertEqual(list_count, notes_count)
