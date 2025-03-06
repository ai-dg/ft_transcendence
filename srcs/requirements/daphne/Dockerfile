FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libpq-dev \
    gcc \
    curl \
    net-tools \
    redis-tools \
    # redis-server \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app/data/

COPY requirements/daphne/conf/requirements.txt /requirements.txt
COPY requirements/daphne/tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

CMD ["/entrypoint.sh"]