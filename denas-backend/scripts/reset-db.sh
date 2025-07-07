#!/bin/bash

# Reset the database
echo "Resetting database..."

# Stop containers
docker-compose down

# Remove database volume
docker volume rm denas-backend_postgres_data

# Start containers
docker-compose up --build -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker-compose exec app alembic upgrade head

echo "Database reset complete!" 