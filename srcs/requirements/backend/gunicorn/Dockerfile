
FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libpq-dev \
    gcc \
    curl \
    nodejs \
    npm \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app/data/

COPY requirements/backend/gunicorn/tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENV PATH="/app/data/venv/bin:$PATH"

CMD ["/entrypoint.sh"]