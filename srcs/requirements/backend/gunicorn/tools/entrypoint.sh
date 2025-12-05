#!/bin/bash

echo -e "\033[35mDjango est en mode : $DJANGO_ENV\033[0m"

source /app/data/venv/bin/activate

#if [ -d "/app/data/static/ts" ]; then
#  echo -e "\033[33mInstallation des dépendances JavaScript...\033[0m"
#  cd /app/data/static/ts
#  npm install
#  npm run build
#  cd -
#fi

sleep 10

echo -e "\033[33mApplication des migrations...\033[0m"
python manage.py makemigrations pong
python manage.py makemigrations accounts
python manage.py makemigrations livechat
python manage.py makemigrations
python manage.py migrate

if [ "$DJANGO_ENV" == "DEV" ]; then
    # echo -e "\033[32mCollecte des fichiers statiques...\033[0m"
    # rm -rf /app/data/staticfiles/*
    # python manage.py collectstatic --noinput
    echo -e "\033[32mDémarrage en mode DEV avec Gunicorn...\033[0m"
    exec gunicorn server.wsgi:application \
        --bind 0.0.0.0:8000 \
        --reload \
        --log-level debug \
        --workers 3
else
    echo -e "\033[32mCollecte des fichiers statiques...\033[0m"
    rm -rf /app/data/staticfiles/*
    python manage.py collectstatic --noinput
    echo -e "\033[32mDémarrage en mode PROD avec Gunicorn...\033[0m"
    exec gunicorn server.wsgi:application --bind 0.0.0.0:8000
fi