FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libpq-dev \
    gcc \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app/data/

ENV PATH="/app/data/venv/bin:$PATH"

CMD ["sleep", "infinity"]