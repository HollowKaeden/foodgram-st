# Фудграм

## Автор

[Артамонов Иван Алексеевич](https://github.com/HollowKaeden)
Email: Vanya200373@yandex.ru
Telegram: [@BlessNT](https://t.me/BlessNT)

## Стек технологий

- Python 3.9
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker, Docker Compose
- Gunicorn, Nginx
- Git, CI/CD

## Установка и запуск проекта

### 1. Клонирование репозитория

Склонируйте репозиторий и перейдите в созданную папку

```bash
git clone https://github.com/HollowKaeden/foodgram-st.git
cd foodgram-st
```

### 2. Создание .env файла

В корне проекта необходимо создать файл `.env` и заполнить его следующими данными:

```env
# Настройки базы данных
POSTGRES_DB=foodgram_db
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram
DB_HOST=db
DB_PORT=5432

# Настройки Django
SECRET_KEY='django-insecure-6cpoclrx#&)zu^kgaacx)arst*x=qwg-8%+4h(2=ak)lvbm2um'
ALLOWED_HOSTS=backend,localhost,127.0.0.1
DEBUG=False
```

### 3. Запуск Docker Compose

Соберите и запустите контейнеры:

```bash
docker compose up --build
```

### 4. Загрузка ингредиентов

После запуска контейнеров выполните в корне проекта:
```bash
docker compose exec backend python manage.py loaddata ingredients_fixture.json
```
После выполнения база данных будет заполнена продуктами для рецептов

### 5. Создание суперпользователя

Создайте администратора для входа в админ-панель:

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Запуск документации API сервера

Запустите контейнер с документацией:

```bash
cd infra
docker compose up
```

### 7. Доступ к приложению

- [**Основной сайт**](http://localhost:8000/)

- [**Админ-панель Django**](http://localhost:8000/admin/)

- [**Документация API сервера**](http://localhost/api/docs/)

## Локальный запуск без Docker

### 1. Установка зависимостей

Создайте виртуальное окружение и установите библиотеки:

```bash
cd backend
py -3.9 -m venv venv
source venv/Scripts/activate # для Windows
# source venv/bin/activate для Linux/Mac
pip install -r requirements.txt
```

### 2. Настройка базы данных в settings.py

Настройте базу данных по вашему усмотрению. Пример настройки:

```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 3. Выполнение миграций

Создайте таблицы в базе данных:

```bash
python manage.py migrate
```

### 4. Загрузка фикстур

Импортируйте продукты:

```bash
python manage.py loaddata ingredients_fixture.json
```

### 5. Запуск сервера

Запустите сервер локально:

```bash
python manage.py runserver
```
