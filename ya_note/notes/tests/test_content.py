from notes.forms import NoteForm
from notes.models import Note
from notes.tests import common


class TestNotesListPage(common.BaseTest):

    def test_note_in_list_for_author(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        response = self.client.get(self.LIST_NOTE)
        if response.context is not None:
            object_list = response.context['object_list']
            list_count = object_list.count()
            notes_count = Note.objects.count()
            self.assertEqual(list_count, notes_count)

    def test_note_page_contains_form(self):
        """На страницы создания и редактирования передаются формы."""
        response_create = self.auth_client.get(self.ADD_NOTE)
        self.assertIn('form', response_create.context)
        self.assertIsInstance(response_create.context['form'], NoteForm)

        response_edit = self.auth_client.get(self.EDIT_NOTE_USER)
        self.assertIn('form', response_edit.context)
        self.assertIsInstance(response_edit.context['form'], NoteForm)


class TestAuthorNotesListPage(common.BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Note.objects.bulk_create(
            Note(title=f'Заметка {index}', text='Просто текст.',
                 author=cls.author, slug=f'{index}')
            for index in range(1, 7)
        )

    def test_note_not_in_list_for_another_user(self):
        """
        В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        response = self.author_client.get(self.LIST_NOTE)
        if response.context is not None:
            object_list = response.context['object_list']
            list_count = object_list.count()
            notes_count = Note.objects.filter(author=self.author).count()
            self.assertEqual(list_count, notes_count)
