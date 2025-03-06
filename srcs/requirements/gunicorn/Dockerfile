FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libpq-dev \
    gcc \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app/data/

COPY requirements/gunicorn/conf/requirements.txt /requirements.txt
COPY requirements/gunicorn/tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]