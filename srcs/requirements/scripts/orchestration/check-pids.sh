#!/bin/bash

PID_FILE="./srcs/logs/pids.txt"

if [ ! -f "$PID_FILE" ]; then
  echo "❌ Pids file doesn't exist."
  exit 1
fi

echo "🔍 Verifying followers..."

while IFS= read -r pid; do
  if ps -p "$pid" > /dev/null 2>&1; then
    echo "✅ PID $pid is running"
  else
    echo "❌ PID $pid is dead"
  fi
done < "$PID_FILE"
