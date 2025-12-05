#!/bin/bash

echo -e "\033[35mDjango est en mode : $DJANGO_ENV\033[0m"

source /app/data/venv/bin/activate

echo -e "\033[32mStarting Daphne...\033[0m"

exec /app/data/venv/bin/daphne -b 0.0.0.0 -p 8001 server.asgi:application