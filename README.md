# Инструкция по запуску проекта

## 1. Создание .env файла

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
DEBUG=False
```

## 2. Запуск docker compose

Выполните команду в корне проекта:
```bash
docker-compose up --build
```

## 3. Заполнение базы данных

После запуска контейнеров выполните в корне проекта:
```bash
./load_data.sh
```
Скрипт заполнит базу данных тестовыми данными, загрузит нужные медиа-файлы

## 4. Доступ к приложению

Основной сайт: http://localhost:8000/
Админ-панель Django: http://localhost:8000/admin/

## 5. Данные для входа

Данные для входа в аккаунт администратора:
admin@example.com
s3cretpassword

Данные для входа в аккаунт пользователя:
iivanov@example.com
ivpassword