FROM debian:latest

ARG DJANGO_ENV=DEV

RUN apt-get update && apt-get install -y \
    nginx \
    openssl \
    curl \
    net-tools

RUN mkdir -p /etc/nginx/ssl

COPY requirements/proxy/nginx/conf/$DJANGO_ENV.conf /etc/nginx/sites-available/default.conf
COPY requirements/proxy/nginx/conf/nginx.conf /etc/nginx/nginx.conf

RUN ln -s /etc/nginx/sites-available/default.conf /etc/nginx/sites-enabled/

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=localhost" \
    && chmod 644 /etc/nginx/ssl/nginx.crt \
    && chmod 644 /etc/nginx/ssl/nginx.key

RUN mkdir -p /app/data

EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]