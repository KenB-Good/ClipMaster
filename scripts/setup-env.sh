
#!/bin/bash

# ClipMaster Environment Setup Script
# Sets up environment variables and configuration

set -e

echo "⚙️  ClipMaster Environment Setup"
echo "==============================="

# Check if .env file exists
if [ -f "/home/ubuntu/clipmaster/.env" ]; then
    echo "⚠️  .env file already exists. Creating backup..."
    cp /home/ubuntu/clipmaster/.env /home/ubuntu/clipmaster/.env.backup.$(date +%s)
fi

# Generate secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Detect if NVIDIA GPU is available
GPU_AVAILABLE="false"
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        GPU_AVAILABLE="true"
        WHISPER_DEVICE="cuda"
        echo "✅ NVIDIA GPU detected"
    else
        WHISPER_DEVICE="cpu"
        echo "⚠️  NVIDIA GPU not available, using CPU"
    fi
else
    WHISPER_DEVICE="cpu"
    echo "⚠️  NVIDIA drivers not installed, using CPU"
fi

# Create comprehensive .env file
cat > /home/ubuntu/clipmaster/.env << EOF
# ===========================================
# ClipMaster Configuration
# ===========================================

# Database Configuration
DATABASE_URL=postgresql://clipmaster:clipmaster_password@postgres:5432/clipmaster

# Redis Configuration
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# File Storage Configuration
UPLOAD_DIR=/app/storage/uploads
CLIPS_DIR=/app/storage/clips
TEMP_DIR=/app/storage/temp
MAX_FILE_SIZE=5368709120

# AI Configuration
WHISPER_MODEL=base
WHISPER_DEVICE=$WHISPER_DEVICE
ENABLE_GPU=$GPU_AVAILABLE

# Processing Configuration
DEFAULT_CLIP_DURATION=30
MIN_HIGHLIGHT_DURATION=5
MAX_HIGHLIGHT_DURATION=120
CONFIDENCE_THRESHOLD=0.7

# Cleanup Configuration
AUTO_CLEANUP_ENABLED=true
AUTO_CLEANUP_DAYS=30
AUTO_CLEANUP_THRESHOLD=0.8

# Security Configuration
SECRET_KEY=$SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=ClipMaster
ALLOWED_HOSTS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Twitch API Configuration
# ⚠️  IMPORTANT: Update these with your Twitch app credentials
# Get them from: https://dev.twitch.tv/console/apps
TWITCH_CLIENT_ID=your_twitch_client_id_here
TWITCH_CLIENT_SECRET=your_twitch_client_secret_here
TWITCH_REDIRECT_URI=http://localhost:3000/twitch/callback

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=$SECRET_KEY

# Logging Configuration
LOG_LEVEL=INFO

# Development Configuration
NODE_ENV=production
PYTHONPATH=/app

# Model Cache Configuration
TORCH_HOME=/app/models
HF_HOME=/app/models
TRANSFORMERS_CACHE=/app/models
EOF

echo "✅ Environment file created: /home/ubuntu/clipmaster/.env"

# Create production environment file
cat > /home/ubuntu/clipmaster/.env.production << EOF
# Production Environment Configuration
# Copy this to .env.production when deploying

# Override for production
NODE_ENV=production
LOG_LEVEL=WARNING
AUTO_CLEANUP_ENABLED=true

# Security (generate new keys for production)
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION
NEXTAUTH_SECRET=CHANGE_THIS_IN_PRODUCTION

# Production URLs (update with your domain)
NEXT_PUBLIC_API_URL=https://your-domain.com
NEXTAUTH_URL=https://your-domain.com
ALLOWED_HOSTS=["https://your-domain.com"]
TWITCH_REDIRECT_URI=https://your-domain.com/twitch/callback

# Production database (consider using managed service)
DATABASE_URL=postgresql://user:password@your-db-host:5432/clipmaster_prod

# Production Redis (consider using managed service)
REDIS_URL=redis://your-redis-host:6379/0
CELERY_BROKER_URL=redis://your-redis-host:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-host:6379/0
EOF

echo "✅ Production environment template created: /home/ubuntu/clipmaster/.env.production"

# Set appropriate permissions
chmod 600 /home/ubuntu/clipmaster/.env
chmod 600 /home/ubuntu/clipmaster/.env.production

# Create configuration validation script
cat > /home/ubuntu/clipmaster/scripts/validate-config.sh << 'EOF'
#!/bin/bash

echo "🔍 Validating ClipMaster Configuration"
echo "====================================="

cd /home/ubuntu/clipmaster

# Source environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found"
    exit 1
fi

# Check database connection
echo "📊 Checking database connection..."
if docker-compose exec -T postgres pg_isready -h postgres -U clipmaster; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi

# Check Redis connection
echo "📊 Checking Redis connection..."
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis connection successful"
else
    echo "❌ Redis connection failed"
fi

# Check storage directories
echo "📁 Checking storage directories..."
for dir in "storage/uploads" "storage/clips" "storage/temp"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing"
        mkdir -p "$dir"
        echo "✅ Created $dir"
    fi
done

# Check Twitch API configuration
echo "🎮 Checking Twitch API configuration..."
if [ "$TWITCH_CLIENT_ID" = "your_twitch_client_id_here" ]; then
    echo "⚠️  Twitch Client ID not configured"
else
    echo "✅ Twitch Client ID configured"
fi

if [ "$TWITCH_CLIENT_SECRET" = "your_twitch_client_secret_here" ]; then
    echo "⚠️  Twitch Client Secret not configured"
else
    echo "✅ Twitch Client Secret configured"
fi

# Check GPU availability
echo "🎮 Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        echo "✅ NVIDIA GPU available"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    else
        echo "⚠️  NVIDIA GPU detected but not accessible"
    fi
else
    echo "⚠️  No NVIDIA GPU detected"
fi

# Check disk space
echo "💾 Checking disk space..."
AVAILABLE=$(df /home/ubuntu/clipmaster/storage | tail -1 | awk '{print $4}')
AVAILABLE_GB=$((AVAILABLE / 1024 / 1024))

if [ $AVAILABLE_GB -lt 10 ]; then
    echo "⚠️  Low disk space: ${AVAILABLE_GB}GB available"
else
    echo "✅ Sufficient disk space: ${AVAILABLE_GB}GB available"
fi

echo ""
echo "🎉 Configuration validation completed"
EOF

chmod +x /home/ubuntu/clipmaster/scripts/validate-config.sh

echo ""
echo "📋 Next steps:"
echo "1. Update Twitch API credentials in .env file:"
echo "   TWITCH_CLIENT_ID=your_actual_client_id"
echo "   TWITCH_CLIENT_SECRET=your_actual_client_secret"
echo ""
echo "2. Validate configuration:"
echo "   ./scripts/validate-config.sh"
echo ""
echo "3. Start ClipMaster:"
echo "   docker-compose up -d"
echo ""
echo "⚠️  Remember to keep your .env file secure and never commit it to version control!"
