#!/bin/bash

set -e

CONF_PATH="./srcs/requirements/elk/logstash/conf/logstash.conf"

cat <<EOF > "$CONF_PATH"
input {
  file {
    path => "/var/lib/docker/containers/*/*.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  mutate {
    add_field => { "origin" => "%{path}" }
    add_field => { "service_name" => "unknown" }
  }

EOF

docker ps -a --format '{{.ID}} {{.Names}}' | while read id name; do
  echo "  if \"$id\" in [path] or \"$id\" in [host] or [host] == \"$id\" {" >> "$CONF_PATH"
  echo "    mutate { replace => { \"service_name\" => \"$name\" } }" >> "$CONF_PATH"
  echo "  }" >> "$CONF_PATH"
done

docker ps -a --no-trunc --format '{{.ID}} {{.Names}}' | while read id name; do
  echo "  if \"$id\" in [path] or \"$id\" in [host] or [host] == \"$id\" {" >> "$CONF_PATH"
  echo "    mutate { replace => { \"service_name\" => \"$name\" } }" >> "$CONF_PATH"
  echo "  }" >> "$CONF_PATH"
done

cat <<'EOF' >> "$CONF_PATH"

  if [service_name] == "unknown" {
    # mutate { add_tag => ["unclassified_log"] }
    # drop { }
  }

  if [log] {
    json {
      source => "log"
      target => "parsed_log"
      skip_on_invalid_json => true
    }
  }

  # Ajout de fallback parsing pour niveau de log (ex: ligne brute)
  if ![parsed_log][levelname] {
    grok {
      match => {
        "log" => [
          "\[%{TIMESTAMP_ISO8601:parsed_log.asctime}\]\[%{LOGLEVEL:parsed_log.levelname}\](\[%{DATA:parsed_log.component}\])?\[%{DATA:parsed_log.context}\](\[%{DATA:parsed_log.id}\])? %{GREEDYDATA:parsed_log.message}",
          "%{TIMESTAMP_ISO8601:parsed_log.asctime} %{LOGLEVEL:parsed_log.levelname} %{GREEDYDATA:parsed_log.message}"
        ]
      }
      overwrite => [ "log" ]
      tag_on_failure => []
    }
  }

  mutate {
    remove_field => ["log", "path", "host", "stream", "@version"]
  }


  # Standardiser le nom du niveau si stocké sous un autre champ
  if [parsed_log][level] and ![parsed_log][levelname] {
    mutate {
      rename => { "[parsed_log][level]" => "[parsed_log][levelname]" }
    }
  }

  # Valeur par défaut si aucun niveau n'est trouvé
  if ![parsed_log][levelname] {
    mutate {
      add_field => { "[parsed_log][levelname]" => "UNSPECIFIED" }
    }
  }

  date {
    match => ["parsed_log.time", "ISO8601"]
    target => "@timestamp"
  }

  date {
    match => ["parsed_log.timestamp", "ISO8601"]
    target => "@timestamp"
  }


  mutate {
    add_field => {
      "[parsed_log][origin]" => "%{origin}"
      "[parsed_log][service_name]" => "%{service_name}"
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "transcendance-filtered"
  }
  # stdout {
  #   codec => rubydebug
  # }
}
EOF