FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/data

COPY requirements/core/dependencies/conf/requirements.txt ./requirements.txt

RUN python3 -m venv /app/data/venv && \
    /app/data/venv/bin/pip install --upgrade pip && \
    /app/data/venv/bin/pip install -r requirements.txt
