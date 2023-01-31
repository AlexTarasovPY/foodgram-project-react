# praktikum_new_diplom

Проект Продуктовый помощник собирает рецепты зарегистрированных пользователей.
Позволяет создавать и редактировать рецепты, добавлять рецепты в избранное, добавлять рецепты в список для покупки ингредиентов с возможностью выгрузки списка в TXT-файл.
Есть возможность подписываться на пользователей.
Рецепты отмечаются тегами, которые устанавливает администратор.

Проект доступен по адресу http://51.250.97.138/
Админ-зона http://51.250.97.138/admin


# Используемые технологии:
Django Rest Framework, docker, nginx, gunicorn, React.
База данных реализована на Postgres.
Требуется установка Docker compose

# Скачать проект:
git clone https://github.com/AlexTarasovPY/foodgram-project-react
# Развернуть проект:
Для развертывания приложения необходим сервер Ubuntu с подключением по SSH.
При выполнении push в гитхаб проект автоматически разворачивается на указанном сервере c помощью GIT Actions.
Образы backend-приложения (Django Rest Framework + gunicorn) и frontend-приложения(React) создаются в workflow и копируются в docker hub.
Необходимые для подключения к серверу, идентификации пользователя и создания базы данных данные вносятся в Actions Secrets (DB_ENGINE, DB_HOST, DB_NAME, DB_PORT, DOCKER_PASSWORD, DOCKER_USERNAME, HOST, PASSPHRASE, POSTGRES_PASSWORD, POSTGRES_USER, SSH_KEY, USER).
На сервер необходимо предварительно скопировать файлы docker-compose.yml и nginx.conf.
Сервис разворачивается в трех контейнерах: backend, postgres и nginx.

После успешного завершения workflow на сервере необходимо создать пользователя:

sudo docker container ls - получаем ID контейнера backend
sudo docker exec -it <ID контейнера> bash - подключаемся к контейнеру
python3 manage.py createsuperuser - создаем суперпользователя и вводим учетные данные


# Автор проекта:
Тарасов Алексей

![yamdb_workflow Actions Status](https://github.com/AlexTarasovPY/foodgram-project-react/actions/workflows/main.yml/badge.svg)]

Проект Продуктовый помощник собирает рецепты зарегистрированных пользователей.
Позволяет создавать и редактировать рецепты, добавлять рецепты в избранное, добавлять рецепты в список для покупки ингредиентов с возможностью выгрузки списка в TXT-файл.
Есть возможность подписываться на пользователей.
Рецепты отмечаются тегами, которые устанавливает администратор.

Проект доступен по адресу http://51.250.97.138/
Админ-зона http://51.250.97.138/admin


# Используемые технологии:
Django Rest Framework, docker, nginx, gunicorn, React.
База данных реализована на Postgres.
Требуется установка Docker compose

# Скачать проект:
git clone https://github.com/AlexTarasovPY/foodgram-project-react
# Развернуть проект:
Для развертывания приложения необходим сервер Ubuntu с подключением по SSH.
При выполнении push в гитхаб проект автоматически разворачивается на указанном сервере c помощью GIT Actions.
Образы backend-приложения (Django Rest Framework + gunicorn) и frontend-приложения(React) создаются в workflow и копируются в docker hub.
Необходимые для подключения к серверу, идентификации пользователя и создания базы данных данные вносятся в Actions Secrets (DB_ENGINE, DB_HOST, DB_NAME, DB_PORT, DOCKER_PASSWORD, DOCKER_USERNAME, HOST, PASSPHRASE, POSTGRES_PASSWORD, POSTGRES_USER, SSH_KEY, USER).
На сервер необходимо предварительно скопировать файлы docker-compose.yml и nginx.conf.
Сервис разворачивается в трех контейнерах: backend, postgres и nginx.

После успешного завершения workflow на сервере необходимо создать пользователя:

sudo docker container ls - получаем ID контейнера backend
sudo docker exec -it <ID контейнера> bash - подключаемся к контейнеру
python3 manage.py createsuperuser - создаем суперпользователя и вводим учетные данные


# Автор проекта:
Тарасов Алексей

![yamdb_workflow Actions Status](https://github.com/AlexTarasovPY/foodgram-project-react/actions/workflows/main.yml/badge.svg)]