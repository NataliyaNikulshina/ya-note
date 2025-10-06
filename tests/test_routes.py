# Импортируем класс HTTPStatus.
from http import HTTPStatus
from django.test import TestCase
# Импортируем функцию reverse().
from django.urls import reverse
# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователей
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')

        # Создаём заметку, указывая автора
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:detail', 'notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления заметки:
                url = reverse(name, args=(self.note.id,))
                # Ожидаемый адрес редиректа:
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект ведёт
                # именно на логин с параметром next.
                self.assertRedirects(response, redirect_url)
