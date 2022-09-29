Foodgram
Проект Foodgram

Адрес

http://51.250.110.215

Описание
Cайт Foodgram - онлайн-сервис, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Проект использует базу данных PostgreSQL. Проект запускается в трёх контейнерах (nginx, PostgreSQL и Django) (контейнер frontend используется лишь для подготовки файлов) через docker-compose на сервере. Образ с проектом загружается на Docker Hub.

Пользовательские роли

Гость (неавторизованный пользователь)
Что могут делать неавторизованные пользователи:

Создать аккаунт.
Просматривать рецепты на главной.
Просматривать отдельные страницы рецептов.
Просматривать страницы пользователей.
Фильтровать рецепты по тегам.

Авторизованный пользователь
Что могут делать авторизованные пользователи:

Входить в систему под своим логином и паролем.
Выходить из системы (разлогиниваться).
Менять свой пароль.
Создавать/редактировать/удалять собственные рецепты
Просматривать рецепты на главной.
Просматривать страницы пользователей.
Просматривать отдельные страницы рецептов.
Фильтровать рецепты по тегам.
Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок.
Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

Администратор
Администратор обладает всеми правами авторизованного пользователя. Плюс к этому он может:

изменять пароль любого пользователя,
создавать/блокировать/удалять аккаунты пользователей,
редактировать/удалять любые рецепты,
добавлять/удалять/редактировать ингредиенты.
добавлять/удалять/редактировать теги.

Ресурсы API Foodgram
Ресурс auth: аутентификация.
Ресурс users: пользователи.
Ресурс tags: получение данных тега или списка тегов рецепта.
Ресурс recipes: создание/редактирование/удаление рецептов, а также получение списка рецептов или данных о рецепте.
Ресурс shopping_cart: добавление/удаление рецептов в список покупок.
Ресурс download_shopping_cart: cкачать файл со списком покупок.
Ресурс favorite: добавление/удаление рецептов в избранное пользователя.
Ресурс subscribe: добавление/удаление пользователя в подписки.
Ресурс subscriptions: возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты.
Ресурс ingredients: получение данных ингредиента или списка ингредиентов.

Шаблон наполнения env-файла
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера) DB_PORT=5432 # порт для подключения к БД

Развёртывание проекта в нескольких контейнерах
Инструкции по развёртыванию проекта в нескольких контейнерах пишут в файле docker-compose.yaml. Убедитесь, что вы находитесь в той же директории, где сохранён docker-compose.yaml и запустите docker-compose командой docker-compose up. У вас развернётся проект, запущенный через Gunicorn с базой данных Postgres.

Стек технологий

asgiref==3.5.2
certifi==2022.6.15
cffi==1.15.1
charset-normalizer==2.1.1
coreapi==2.3.3
coreschema==0.0.4
cryptography==37.0.4
defusedxml==0.7.1
Django==3.2.15
django-filter==22.1
django-templated-mail==1.1.1
djangorestframework==3.13.1
djangorestframework-simplejwt==4.7.2
djoser==2.1.0
drf-extra-fields==3.4.0
idna==3.3
importlib-metadata==1.7.0
isort==5.10.1
itypes==1.2.0
Jinja2==3.1.2
MarkupSafe==2.1.1
oauthlib==3.2.0
Pillow==9.2.0
psycopg2-binary==2.9.3
pycparser==2.21
PyJWT==2.4.0
python-dotenv==0.20.0
python3-openid==3.2.0
pytz==2022.2.1
requests==2.28.1
requests-oauthlib==1.3.1
six==1.16.0
social-auth-app-django==4.0.0
social-auth-core==4.3.0
sqlparse==0.4.2
typing_extensions==4.3.0
uritemplate==4.1.1
urllib3==1.26.12
zipp==3.8.1

Примеры
Примеры запросов по API:

[GET] /api/users/ - Получить список всех пользователей.
[POST] /api/users/ - Регистрация пользователя.
[GET] /api/tags/ - Получить список всех тегов.
[POST] /api/recipes/ - Создание рецепта.
[GET] /api/recipes/download_shopping_cart/ - Скачать файл со списком покупок.
[POST] /api/recipes/{id}/favorite/ - Добавить рецепт в избранное.
[DEL] /api/users/{id}/subscribe/ - Отписаться от пользователя.
[GET] /api/ingredients/ - Список ингредиентов с возможностью поиска по имени.

Автор
Никита Цыбин https://github.com/kellia1903