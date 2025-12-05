FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    net-tools \
    redis-tools \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app/data/

COPY requirements/backend/daphne/tools/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8001

CMD ["/entrypoint.sh"]