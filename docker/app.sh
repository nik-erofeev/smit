#!/bin/bash


echo "Waiting for 1 seconds to allow PostgreSQL to start..."
sleep 1

echo "Starting migrations..."
alembic upgrade head
MIGRATION_STATUS=$?
if [ $MIGRATION_STATUS -ne 0 ]; then
  echo "Migrations failed with status $MIGRATION_STATUS"
  exit 1
fi

## статического ожидание вместо (nc -z kafka) так же убрать из dockerfile (netcat-openbsd) если не используется
# echo "Waiting for Kafka to start..."
# sleep 10

echo "Waiting for Kafka to start..."
while ! nc -z kafka 9092; do
  sleep 1
done

echo "Starting FastAPI server..."
python main.py