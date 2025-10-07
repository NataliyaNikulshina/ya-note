# notes/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NOTE_TITLE = 'Заголовок заметки'

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователя и логиним его
        cls.user = User.objects.create(username='Автор заметки')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        # URL для создания и списка заметок
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')

        # Данные для POST-запроса создания заметки
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': slugify(cls.NOTE_TITLE),
        }

    def test_anonymous_user_cant_create_note(self):
        """Аноним не может создать заметку."""
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_authenticated_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.auth_client.post(self.add_url, data=self.form_data)
        # После успешного создания редирект идёт на страницу успеха
        success_url = reverse('notes:success')
        self.assertRedirects(response, success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Исходный текст'
    UPDATED_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        # Автор заметки
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        # Другой пользователь
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        # Создаём заметку
        cls.note = Note.objects.create(
            title='Моя заметка',
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='moya-zametka',
        )

        # Формируем URL'ы для редактирования и удаления
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.form_data = {'title': cls.note.title, 'text': cls.UPDATED_TEXT, 
                         'slug': cls.note.slug}

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.UPDATED_TEXT)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_other_user_cant_edit_note(self):
        """Другой пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалить чужую заметку."""
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
