
#!/bin/bash

# ClipMaster Quick Start Script
# This script performs a complete setup and starts ClipMaster

set -e

echo "🎬 ClipMaster Quick Start"
echo "========================"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the ClipMaster root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please run scripts/install.sh first"
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please run scripts/install.sh first"
    exit 1
fi

echo "✅ Prerequisites met"

# Set up environment if not exists
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment..."
    ./scripts/setup-env.sh
else
    echo "✅ Environment file exists"
fi

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p storage/{uploads,clips,temp}
mkdir -p models
echo "✅ Storage directories created"

# Check if containers are already running
if docker-compose ps | grep -q "Up"; then
    echo "⚠️  Some containers are already running. Stopping them first..."
    docker-compose down
fi

# Pull/build images
echo "📦 Building Docker images..."
docker-compose build --parallel

# Start services
echo "🚀 Starting ClipMaster services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check database
echo -n "📊 Database: "
if docker-compose exec -T postgres pg_isready -h localhost -U clipmaster > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ Not ready"
    echo "💡 This might take a few more seconds on first startup..."
fi

# Check Redis
echo -n "🔴 Redis: "
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Ready"
else
    echo "❌ Not ready"
fi

# Check API
echo -n "🌐 API: "
sleep 5  # Give API a moment to start
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ Not ready (this is normal on first startup)"
fi

# Check Frontend
echo -n "🖥️  Frontend: "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ Not ready (this is normal on first startup)"
fi

echo ""
echo "🎉 ClipMaster startup completed!"
echo ""
echo "📋 Service Status:"
docker-compose ps

echo ""
echo "🌐 Access URLs:"
echo "• Frontend: http://localhost:3000"
echo "• API: http://localhost:8000"
echo "• API Docs: http://localhost:8000/docs"
echo "• Flower (Task Monitor): http://localhost:5555"

echo ""
echo "📊 System Status:"
echo "• Storage: $(df -h storage | tail -1 | awk '{print $4}') available"
echo "• Memory: $(free -h | grep Mem | awk '{print $7}') available"

if command_exists nvidia-smi; then
    if nvidia-smi > /dev/null 2>&1; then
        echo "• GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)"
    fi
fi

echo ""
echo "🛠️  Useful Commands:"
echo "• View logs: docker-compose logs -f"
echo "• Stop services: docker-compose down"
echo "• Restart services: docker-compose restart"
echo "• Monitor system: ./monitor.sh"
echo "• Update: ./update.sh"
echo "• Backup: ./backup.sh"

echo ""
echo "⚙️  Configuration:"
if grep -q "your_twitch_client_id_here" .env 2>/dev/null; then
    echo "⚠️  Please configure your Twitch API credentials in .env file"
    echo "   Get them from: https://dev.twitch.tv/console/apps"
else
    echo "✅ Twitch API credentials configured"
fi

echo ""
echo "📚 Next Steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Upload a video or connect your Twitch account"
echo "3. Watch the AI process your content!"
echo ""
echo "🆘 Need help? Check the logs: docker-compose logs -f"
