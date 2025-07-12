#!/bin/bash

# Script to run FastAPI with different environment configurations
# Usage: ./scripts/run-with-env.sh [local|supabase|production]

ENV_TYPE=${1:-local}

echo "🚀 Starting Denas Backend with $ENV_TYPE environment..."

# Validate environment type
if [[ ! "$ENV_TYPE" =~ ^(local|supabase|production)$ ]]; then
    echo "❌ Invalid environment type: $ENV_TYPE"
    echo "Valid options: local, supabase, production"
    exit 1
fi

# Check if env file exists
ENV_FILE="env/.env.$ENV_TYPE"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ Environment file not found: $ENV_FILE"
    exit 1
fi

echo "📄 Using environment file: $ENV_FILE"

# Set the DB_ENV variable and run the application
export DB_ENV=$ENV_TYPE
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo "🔄 Application stopped." 