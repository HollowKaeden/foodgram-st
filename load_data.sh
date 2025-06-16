#!/bin/bash

echo "Загружаем медиа-файлы в volume..."

docker cp ./media_backup/. $(docker-compose ps -q backend):/app/media/

echo "Готово."

echo "Загружаем фикстуры в базу данных..."

docker-compose exec backend python manage.py loaddata fixtures.json

echo "Готово."
