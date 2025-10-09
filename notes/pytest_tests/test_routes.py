# test_routes.py
from http import HTTPStatus
import pytest
from pytest_lazy_fixtures import lf
from django.urls import reverse
from pytest_django.asserts import assertRedirects
# from notes.models import Note

# Проверим, что анонимному пользователю 
# доступна главная страница проекта.
# Указываем в фикстурах встроенный клиент.
# def test_home_availability_for_anonymous_user(client):
#     # Адрес страницы получаем через reverse():
#     url = reverse('notes:home')
#     response = client.get(url)
#     assert response.status_code == HTTPStatus.OK

# Проверим, что анонимному пользователю 
# доступна главная страница проекта, страницы входа 
# и выхода(страниц логина, логаута и регистрации).


@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('notes:home', 'users:login', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# Тестирование доступности страниц
# для авторизованного пользователя


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


# # Проверим, что автору заметки доступны страницы отдельной заметки,
# # её редактирования и удаления
# @pytest.mark.parametrize(
#     'name',
#     ('notes:detail', 'notes:edit', 'notes:delete'),
# )
# def test_pages_availability_for_author(author_client, name, note):
#     url = reverse(name, args=(note.slug,))
#     response = author_client.get(url)
#     assert response.status_code == HTTPStatus.OK


# def test_note_exists(note):
#     notes_count = Note.objects.count()
#     # Общее количество заметок в БД равно 1.
#     assert notes_count == 1
#     # Заголовок объекта, полученного при помощи фикстуры note,
#     # совпадает с тем, что указан в фикстуре.
#     assert note.title == 'Заголовок'


# # Обозначаем, что тесту нужен доступ к БД.
# # Без этой метки тест выдаст ошибку доступа к БД.
# @pytest.mark.django_db
# def test_empty_db():
#     notes_count = Note.objects.count()
#     # В пустой БД никаких заметок не будет:
#     assert notes_count == 0

# проверить, что пользователю, залогиненному в клиенте not_author_client
# (не автору заметки), при запросе к страницам 'notes:detail', 'notes:edit'
# и 'notes:delete' возвращается ошибка 404
# Вложенные параметры

@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ],
)
# Этот декоратор оставляем таким же, как в предыдущем тесте.
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
# В параметры теста добавляем имена parametrized_client и expected_status.
def test_pages_availability_for_different_users(
        parametrized_client, name, note, expected_status
):
    """
    Проверяем доступность страниц заметок, резактирования и удаления
    для автора и чужого пользователя.
    - Автор должен получать 200 (OK)
    - Не автор — 404 (NOT FOUND)
    """
    url = reverse(name, args=(note.slug,))
    # Делаем запрос от имени клиента parametrized_client:
    response = parametrized_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    # Вторым параметром передаём note_object,
    # в котором будет либо фикстура с объектом заметки, либо None.
    'name, args',
    (
        ('notes:detail', lf('slug_for_args')),
        ('notes:edit', lf('slug_for_args')),
        ('notes:delete', lf('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
def test_redirects(client, name, args):
    """
    Проверяет, что анонимный пользователь перенаправляется на страницу логина 
    при попытке открыть любую страницу, доступную только авторизованным 
    пользователям.

    Для страниц, связанных с конкретной заметкой (detail, edit, delete),
    используется slug заметки из фикстуры note_object.
    Для остальных страниц (add, success, list) аргументы не требуются.

    Ожидается редирект на URL:
        /auth/login/?next=<адрес_запрошенной_страницы>
    """
    login_url = reverse('users:login')
    # Формируем URL в зависимости от того, передан ли объект заметки:
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
