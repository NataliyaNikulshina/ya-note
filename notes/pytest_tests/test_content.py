# test_content.py
import pytest
from pytest_lazy_fixtures import lf
from django.urls import reverse

from notes.forms import NoteForm

# # В тесте используем фикстуру заметки
# # и фикстуру клиента с автором заметки.
# def test_note_in_list_for_author(note, author_client):
#     url = reverse('notes:list')
#     # Запрашиваем страницу со списком заметок:
#     response = author_client.get(url)
#     # Получаем список объектов из контекста:
#     object_list = response.context['object_list']
#     # Проверяем, что заметка находится в этом списке:
#     assert note in object_list


# # В этом тесте тоже используем фикстуру заметки,
# # но в качестве клиента используем not_author_client;
# # в этом клиенте авторизован не автор заметки, 
# # так что заметка не должна быть ему видна.
# def test_note_not_in_list_for_another_user(note, not_author_client):
#     url = reverse('notes:list')
#     response = not_author_client.get(url)
#     object_list = response.context['object_list']
#     # Проверяем, что заметки нет в контексте страницы:
#     assert note not in object_list

@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, note_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (lf('author_client'), True),
        (lf('not_author_client'), False),
    )
)
# Используем фикстуру заметки и параметры из декоратора:
def test_notes_list_for_different_users(
    note, parametrized_client, note_in_list
):
    """Отдельная заметка передаётся на страницу со списком заметок
    в списке object_list, в словаре context;
    в список заметок одного пользователя не попадают заметки 
    другого пользователя;
    """
    url = reverse('notes:list')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    # В качестве параметров передаём name и args для reverse.
    'name, args',
    (
        # Для тестирования страницы создания заметки
        # никакие дополнительные аргументы для reverse() не нужны.
        ('notes:add', None),
        # Для тестирования страницы редактирования заметки нужен slug заметки.
        ('notes:edit', lf('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    """Проверка передаются ли формы на страницы создания
    и редактирования заметки
    """
    # Формируем URL.
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm)