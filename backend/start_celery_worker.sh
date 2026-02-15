#!/bin/bash
# Start Celery Worker
# Run this in a separate terminal window

echo "🚀 Starting Celery Worker..."
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Make sure we're in the backend directory
if [ ! -d "app" ]; then
    echo "❌ Error: Must run from backend directory"
    exit 1
fi

# Check if Redis is running
if ! nc -z localhost 6379 2>/dev/null; then
    echo "⚠️  Warning: Redis doesn't seem to be running on port 6379"
    echo "   Start it with: docker-compose up -d redis"
    echo ""
fi

# Start Celery worker
echo "📡 Starting Celery worker..."
echo "   Press Ctrl+C to stop"
echo ""

celery -A app.workers.celery_app worker --loglevel=info --pool=solo
