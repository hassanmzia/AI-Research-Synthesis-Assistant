#!/bin/bash
set -e

echo "========================================"
echo " AI Research Synthesis Assistant"
echo " Starting all services..."
echo "========================================"

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "WARNING: Please set your OPENAI_API_KEY in .env"
fi

# Build and start all services
docker compose build --parallel
docker compose up -d

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
until docker compose exec -T postgres pg_isready -U arsa_user -d research_assistant 2>/dev/null; do
    sleep 2
done
echo "PostgreSQL is ready."

# Run Django migrations
echo "Running database migrations..."
docker compose exec -T backend python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
docker compose exec -T backend python manage.py collectstatic --noinput 2>/dev/null || true

# Setup initial data
echo "Setting up initial data..."
docker compose exec -T backend python manage.py setup_initial_data

echo ""
echo "========================================"
echo " All services are running!"
echo "========================================"
echo ""
echo " Main Site:       http://172.168.1.95:3066"
echo " Django Admin:    http://172.168.1.95:3066/admin/"
echo " API Gateway:     http://172.168.1.95:3067"
echo " Django Backend:  http://172.168.1.95:3070"
echo " Celery Flower:   http://172.168.1.95:5556"
echo " PostgreSQL:      172.168.1.95:5434"
echo " Redis:           172.168.1.95:6381"
echo " ChromaDB:        http://172.168.1.95:8101"
echo ""
echo " MCP Endpoint:    http://172.168.1.95:3066/mcp/"
echo " A2A Endpoint:    http://172.168.1.95:3066/a2a/"
echo " API Docs:        http://172.168.1.95:3066/api/"
echo ""
echo " Default Users:"
echo "   Admin:      admin / admin123"
echo "   Researcher: researcher / research123"
echo ""
echo "========================================"
