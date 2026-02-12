#!/bin/bash

echo "🚀 Starting TikTok Pipeline V2.1 (Local Development)"
echo ""

# Check credentials
if [ ! -f "./backend/credentials.json" ]; then
    echo "⚠️  WARNING: backend/credentials.json not found!"
    echo "   Please add your GCP service account credentials"
    echo ""
fi

# Build and start
echo "📦 Building and starting containers..."
docker-compose up -d --build

echo ""
echo "✅ Containers started!"
echo ""
echo "📍 Services:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 View logs:    docker-compose logs -f"
echo "🛑 Stop:         docker-compose down"
echo ""
