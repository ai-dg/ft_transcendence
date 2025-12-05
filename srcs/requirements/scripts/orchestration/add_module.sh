#!/bin/bash

PROJECT_PATH="srcs/backend"

if [ "$1" ]; then
    echo "Création de l'application Django : $1"
    cd "$PROJECT_PATH" || exit 1
    ./venv/bin/python3 manage.py startapp "$1" 
else
    echo "Erreur : Veuillez spécifier un nom d'application."
    exit 1
fi