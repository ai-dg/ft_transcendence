FROM debian:11

RUN apt-get update && apt-get install -y \
    redis-server procps

COPY requirements/core/redis/conf/redis.conf /etc/redis/redis.conf
COPY requirements/core/redis/tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN chmod 644 /etc/redis/redis.conf

ENTRYPOINT ["/entrypoint.sh"]