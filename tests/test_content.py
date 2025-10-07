from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm
from django.utils.text import slugify

from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):
    URL = reverse('notes:list')
    URL_ADD = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый автор')

        # Создаём 10 заметок с уникальными slug
        notes_list = []
        for i in range(settings.COUNT_ON_LIST_PAGE):
            title = f'Запись {i}'
            notes_list.append(
                Note(
                    title=title,
                    text='Просто текст.',
                    author=cls.author,
                    slug=slugify(title),  # уникальный slug
                )
            )

        Note.objects.bulk_create(notes_list)
        cls.note = notes_list[0]
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_note_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.URL)
        object_list = response.context['notes_feed']
        news_count = object_list.count()
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(news_count, settings.COUNT_ON_LIST_PAGE)

    def test_note_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.URL)
        notes = response.context['notes_feed']
        titles = [note.title for note in notes]
        sorted_titles = sorted(titles)
        # Проверим, что список заметок отсортирован по алфавиту
        self.assertEqual(titles, sorted_titles)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        # Проверяем, что аноним перенаправляется на логин
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.url)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.URL_ADD)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
