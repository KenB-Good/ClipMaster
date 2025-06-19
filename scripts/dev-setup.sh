
#!/bin/bash

# ClipMaster Development Setup Script
# Sets up development environment with hot reloading

set -e

echo "🛠️  ClipMaster Development Setup"
echo "==============================="

# Check if we're in the right directory
if [ ! -f "docker-compose.dev.yml" ]; then
    echo "❌ Please run this script from the ClipMaster root directory"
    exit 1
fi

# Set up development environment
echo "⚙️  Setting up development environment..."

# Create development environment file
cat > .env.dev << EOF
# Development Environment
NODE_ENV=development
DATABASE_URL=postgresql://clipmaster:clipmaster_password@localhost:5432/clipmaster_dev
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
NEXT_PUBLIC_API_URL=http://localhost:8000
LOG_LEVEL=DEBUG
UPLOAD_DIR=/app/storage/uploads
CLIPS_DIR=/app/storage/clips
TEMP_DIR=/app/storage/temp
WHISPER_MODEL=tiny
ENABLE_GPU=false
SECRET_KEY=dev-secret-key
TWITCH_CLIENT_ID=your_twitch_client_id_here
TWITCH_CLIENT_SECRET=your_twitch_client_secret_here
EOF

# Create storage directories
mkdir -p storage/{uploads,clips,temp}
mkdir -p models

# Stop any running production containers
if docker-compose ps | grep -q "Up"; then
    echo "🛑 Stopping production containers..."
    docker-compose down
fi

# Start development services
echo "🚀 Starting development environment..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

# Show status
echo "📊 Development Environment Status:"
docker-compose -f docker-compose.dev.yml ps

echo ""
echo "🎉 Development environment ready!"
echo ""
echo "🌐 Development URLs:"
echo "• Frontend: http://localhost:3000 (with hot reload)"
echo "• API: http://localhost:8000 (with auto-reload)"
echo "• API Docs: http://localhost:8000/docs"
echo "• Flower: http://localhost:5555"
echo "• Database: localhost:5432"
echo "• Redis: localhost:6379"

echo ""
echo "🛠️  Development Commands:"
echo "• View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "• Stop: docker-compose -f docker-compose.dev.yml down"
echo "• Restart: docker-compose -f docker-compose.dev.yml restart"
echo "• Shell into API: docker-compose -f docker-compose.dev.yml exec api bash"
echo "• Shell into Frontend: docker-compose -f docker-compose.dev.yml exec frontend sh"

echo ""
echo "📝 Development Notes:"
echo "• Code changes will automatically reload"
echo "• Database is separate from production (clipmaster_dev)"
echo "• Using tiny Whisper model for faster development"
echo "• GPU processing disabled by default"
echo "• Debug logging enabled"

echo ""
echo "🔧 To enable GPU in development:"
echo "1. Set ENABLE_GPU=true in .env.dev"
echo "2. Set WHISPER_MODEL=base in .env.dev"
echo "3. Restart: docker-compose -f docker-compose.dev.yml restart"
