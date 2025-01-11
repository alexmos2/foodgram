Адрес foodgram https://taskialexmos.zapto.org
Данные администратора:
email a@a.ru
username alexmos
пароль 314password


Foodgram- проект для публикации рецептов блюд. Можно публиковать рецепты, подписываться на других пользователей и добавлять рецепты в избранное, а также составлять продуктовую корзину со списком нужных ингредиентов.

Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

Примеры запросов:
api/users список пользователей
api/tags список тегов
api/recipes рецепты(например, создание рецепта, пример запроса: 
{
    "ingredients": [
        {
            "id": 1,
            "amount": 10
        },
        {
            "id": 2,
            "amount": 20
        }
    ],
    "tags": [
        1,
        2
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "Нечто съедобное (это не точно)",
    "text": "Приготовьте как нибудь эти ингредиеты",
    "cooking_time": 5
}
)
api/users/subscriptions подписки пользователей (чтобы подписаться, нужен пустой запрос на api/users/{N}/subscribe, где N это id пользователя)

Список использованных библиотек
Django
djangorestframework
django-filter
djoser
Pillow
pytest
pytest-django
pytest-pythonpath
python-dotenv
gunicorn
django-cors-headers
psycopg2-binary
PyYAML
django-core
pyshorteners
