from http import HTTPStatus

from notes.tests import common


class TestRoutes(common.BaseTest):

    def test_pages_availability_for_different_users(self):
        """Проверка доступности страниц разным пользователям."""
        users = (self.author_client, self.reader_client, self.client)
        for user in users:
            for url in self.URLS:
                response = user.get(url)
                with self.subTest(user=user, url=url):
                    if url in self.URLS_FOR_ANONYMOUS_USER and \
                            user == self.client:
                        self.assertEqual(response.status_code, HTTPStatus.OK)
                    if url in self.URLS_NOT_FOR_READER and \
                            user == self.reader_client:
                        self.assertEqual(response.status_code,
                                         HTTPStatus.NOT_FOUND)
                    if user == self.author_client:
                        self.assertEqual(response.status_code, HTTPStatus.OK)

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
            with self.subTest():
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
