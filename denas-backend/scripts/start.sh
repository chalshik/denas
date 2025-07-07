#!/bin/bash

# Start the development environment
echo "Starting Denas Backend Development Environment..."

# Build and start containers
docker-compose up --build -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker-compose exec app alembic upgrade head

echo "Development environment is ready!"
echo "API available at: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo "Database available at: localhost:5432" 