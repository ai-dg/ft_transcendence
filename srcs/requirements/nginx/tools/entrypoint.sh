#!/bin/bash

echo -e "\033[35mDjango est en mode : $DJANGO_ENV\033[0m"

if [ $DJANGO_ENV == "DEV" ]; then
    echo -e "\033[32mStarting in DEV MODE...\033[0m"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo -e "\033[32mStarting in PROD MODE...\033[0m"    
    exec /app/data/venv/bin/gunicorn server.wsgi:application --bind 0.0.0.0:8000
fi
