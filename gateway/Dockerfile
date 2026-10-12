# Прод-шлюз Фудграма: nginx со сборкой React, статикой Django и проксированием на бэкенд.
# Собирается из корня репозитория: docker build -f gateway/Dockerfile .
# Локальная разработка по-прежнему идёт через docker-compose.yml и nginx/.

# 1. Сборка фронтенда (версия Node как в frontend/Dockerfile)
FROM node:21.7.1-alpine AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 2. Статика Django: админка и DRF (версия Python как в backend/Dockerfile)
FROM python:3.9.13-slim AS django-static
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY backend/ .
RUN python manage.py collectstatic --noinput

# 3. nginx (версия как в nginx/Dockerfile, сборка alpine: образ в разы меньше)
FROM nginx:1.22.1-alpine
COPY gateway/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend /app/build /usr/share/nginx/html
# Django кладёт admin/ и rest_framework/ в static/, рядом с js/ и css/ фронтенда: имена не пересекаются
COPY --from=django-static /app/staticfiles/static /usr/share/nginx/html/static
