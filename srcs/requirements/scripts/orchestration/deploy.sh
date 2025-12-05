#!/bin/bash


if [ ! -d '~/data/database' ]; then
    mkdir -p ~/data/database
    mkdir -p ~/data/logsdata
    mkdir -p ./srcs/app/venv
    mkdir -p ./srcs/logs
    cp ./srcs/.env ./srcs/app/
fi

echo -e "\033[32m~/data/database created\033[0m"

