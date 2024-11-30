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

echo "Starting FastAPI server..."
python main.py