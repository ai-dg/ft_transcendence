FROM debian:latest

RUN apt-get update && apt-get install -y \
    redis-server redis-tools

WORKDIR /app/data/

COPY requirements/redis/conf/redis.conf /etc/redis/redis.conf

EXPOSE 6379

CMD ["redis-server", "/etc/redis/redis.conf"]
