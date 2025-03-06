FROM debian:latest

RUN apt-get update && apt-get install -y \
nodejs npm

COPY requirements/nodejs/tools/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app/nodejs/

EXPOSE 8080

CMD ["/entrypoint.sh"]

