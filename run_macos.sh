#!/bin/bash

echo "Starting Kafka"
docker compose up -d

sleep 3

PROJECT_PATH="$(pwd)"

echo "Launching a new terminal with the consumer"
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_PATH'; source venv/bin/activate; python -m consumer.consumer_faust worker -l info"
end tell
EOF

sleep 2

echo "Launching a new terminal with the producer"
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_PATH'; source venv/bin/activate; python -m producer.producer"
end tell
EOF
