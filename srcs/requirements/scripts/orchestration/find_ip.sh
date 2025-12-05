#!/bin/bash

IP=$(ip route get 1.1.1.1 | awk '{print $7; exit}')
if grep -q '^ALLOWED_IP=' ./srcs/.env; then
    sed -i "s/^ALLOWED_IP=.*/ALLOWED_IP=$IP/" ./srcs/.env
else
    echo "ALLOWED_IP=$IP" >> ./srcs/.env
fi
