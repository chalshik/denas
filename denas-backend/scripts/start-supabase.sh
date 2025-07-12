#!/bin/bash

# Script to start Denas Backend with Supabase configuration
echo "🚀 Starting Denas Backend with Supabase configuration..."

# Set environment for Supabase
export DB_ENV=supabase

# Check if Supabase env file exists
if [[ ! -f "env/.env.supabase" ]]; then
    echo "❌ Supabase environment file not found: env/.env.supabase"
    exit 1
fi

echo "📄 Using Supabase environment configuration"
echo "🗄️  Database: Supabase PostgreSQL"
echo "🗂️  Storage: Supabase Storage"

# Start services
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo "🌐 API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "🔍 Health Check: http://localhost:8000/health"
    echo ""
    echo "🗂️  Supabase Storage bucket: product-images"
    echo "📤 Upload endpoints:"
    echo "   - POST /api/v1/uploads/single"
    echo "   - POST /api/v1/uploads/multiple"
    echo "   - POST /api/v1/uploads/product-images"
    echo ""
    echo "To stop services: docker-compose down"
else
    echo "❌ Failed to start services"
    docker-compose logs
    exit 1
fi 