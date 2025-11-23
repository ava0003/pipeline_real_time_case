@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo Starting Kafka
docker compose up -d

echo Waiting for Kafka to start
timeout /t 3 > nul

REM Get absolute path of the project
SET PROJECT_PATH=%cd%

echo Launching a new terminal with the consumer
start cmd /k "cd /d %PROJECT_PATH% && call venv\Scripts\activate && python -m consumer.consumer_faust worker -l info"

timeout /t 2 > nul

echo Launching a new terminal with the producer
start cmd /k "cd /d %PROJECT_PATH% && call venv\Scripts\activate && python -m producer.producer"

echo ✨ All components launched!
ENDLOCAL
