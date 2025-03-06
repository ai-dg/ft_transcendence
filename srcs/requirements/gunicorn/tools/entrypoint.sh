#!/bin/bash

echo "alias python='/app/data/venv/bin/python'" >> ~/.bashrc
echo "alias pip='/app/data/venv/bin/pip'" >> ~/.bashrc

echo -e "\033[35mDjango est en mode : $DJANGO_ENV\033[0m"

if [ ! -d "/app/data/venv" ]; then
    echo -e "\033[33mCréation de l'environnement virtuel...\033[0m"
    python3 -m venv /app/data/venv
    /app/data/venv/bin/pip install --upgrade pip
    /app/data/venv/bin/pip install -r /requirements.txt
fi

source /app/data/venv/bin/activate

echo -e "\033[32mApplying migrations...\033[0m"
/app/data/venv/bin/python manage.py makemigrations
/app/data/venv/bin/python manage.py migrate

if [ "$DJANGO_ENV" == "DEV" ]; then
    echo -e "\033[32mStarting in DEV MODE...\033[0m"
    exec /app/data/venv/bin/python manage.py runserver 0.0.0.0:8000
else
    echo -e "\033[32mCollecting static files...\033[0m"
    /app/data/venv/bin/python manage.py collectstatic --noinput
    echo -e "\033[32mStarting in PROD MODE...\033[0m"
    exec /app/data/venv/bin/gunicorn server.wsgi:application --bind 0.0.0.0:8000
fi
