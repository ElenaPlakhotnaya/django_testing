from http import HTTPStatus

from notes.tests import common


class TestRoutes(common.BaseTest):

    def test_pages_availability_for_different_users(self):
        """Проверка доступности страниц разным пользователям."""
        test_data = [
            (self.HOME_PAGE, self.auth_client, HTTPStatus.OK),
            (self.LOGIN, self.auth_client, HTTPStatus.OK),
            (self.LOGOUT, self.auth_client, HTTPStatus.OK),
            (self.SIGNUP, self.auth_client, HTTPStatus.OK),
            (self.DETAIL_NOTE, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.EDIT_NOTE, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.DELETE_NOTE, self.reader_client, HTTPStatus.NOT_FOUND),
        ]

        for url, user, status in test_data:
            with self.subTest(user=user, url=url, status=status):
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        При попытке перейти на страницу списка заметок,
        страницу успешного добавления записи,
        страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки
        анонимный пользователь перенаправляется на страницу логина.
        """
        login_url = self.LOGIN

        for url in self.URLS_FOR_REDIRECT:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
