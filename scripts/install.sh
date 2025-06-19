
#!/bin/bash

# ClipMaster Installation Script for Ubuntu
# This script installs all dependencies and sets up ClipMaster

set -e

echo "🎬 ClipMaster Installation Script"
echo "=================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Check Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs)
echo "📋 Detected Ubuntu version: $UBUNTU_VERSION"

if [[ "$UBUNTU_VERSION" < "20.04" ]]; then
    echo "❌ Ubuntu 20.04 or higher is required"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Install NVIDIA Docker (for GPU support)
echo "🎮 Setting up NVIDIA Docker for GPU support..."
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 NVIDIA GPU detected, installing NVIDIA Docker..."
    
    # Add NVIDIA Docker repository
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    
    sudo apt update
    sudo apt install -y nvidia-docker2
    sudo systemctl restart docker
    
    echo "✅ NVIDIA Docker installed"
else
    echo "⚠️  No NVIDIA GPU detected, skipping NVIDIA Docker installation"
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y \
    curl \
    git \
    wget \
    unzip \
    htop \
    tree \
    jq \
    ffmpeg \
    streamlink \
    python3-pip \
    nodejs \
    npm

# Install Node.js 18 (LTS)
echo "📦 Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Yarn
echo "📦 Installing Yarn..."
if ! command -v yarn &> /dev/null; then
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
    sudo apt update && sudo apt install -y yarn
    echo "✅ Yarn installed"
else
    echo "✅ Yarn already installed"
fi

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p /home/ubuntu/clipmaster/storage/{uploads,clips,temp}
mkdir -p /home/ubuntu/clipmaster/models

# Set up environment file
echo "⚙️  Setting up environment configuration..."
cat > /home/ubuntu/clipmaster/.env << EOF
# Database
DATABASE_URL=postgresql://clipmaster:clipmaster_password@localhost:5432/clipmaster

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Storage
UPLOAD_DIR=/home/ubuntu/clipmaster/storage/uploads
CLIPS_DIR=/home/ubuntu/clipmaster/storage/clips
TEMP_DIR=/home/ubuntu/clipmaster/storage/temp

# AI Models
WHISPER_MODEL=base
WHISPER_DEVICE=cuda
ENABLE_GPU=true

# Twitch API (Configure these with your Twitch app credentials)
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
TWITCH_REDIRECT_URI=http://localhost:3000/twitch/callback

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# Logging
LOG_LEVEL=INFO
EOF

echo "✅ Environment file created at /home/ubuntu/clipmaster/.env"
echo "⚠️  Please update the Twitch API credentials in the .env file"

# Set up systemd services
echo "⚙️  Setting up systemd services..."

# ClipMaster service
sudo tee /etc/systemd/system/clipmaster.service > /dev/null << EOF
[Unit]
Description=ClipMaster AI Video Processing System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/clipmaster
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu
Group=docker

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable clipmaster

echo "✅ ClipMaster systemd service installed"

# Install useful utilities
echo "🛠️  Installing additional utilities..."

# Install btop (better htop)
if ! command -v btop &> /dev/null; then
    wget https://github.com/aristocratos/btop/releases/latest/download/btop-x86_64-linux-musl.tbz
    tar -xjf btop-x86_64-linux-musl.tbz
    sudo cp btop/bin/btop /usr/local/bin/
    rm -rf btop btop-x86_64-linux-musl.tbz
    echo "✅ btop installed"
fi

# Install nvidia-ml-py for GPU monitoring (if NVIDIA GPU present)
if command -v nvidia-smi &> /dev/null; then
    pip3 install nvidia-ml-py
    echo "✅ NVIDIA monitoring tools installed"
fi

# Set up useful aliases
echo "⚙️  Setting up useful aliases..."
cat >> ~/.bashrc << EOF

# ClipMaster aliases
alias cm-start='cd /home/ubuntu/clipmaster && sudo systemctl start clipmaster'
alias cm-stop='cd /home/ubuntu/clipmaster && sudo systemctl stop clipmaster'
alias cm-restart='cd /home/ubuntu/clipmaster && sudo systemctl restart clipmaster'
alias cm-status='cd /home/ubuntu/clipmaster && sudo systemctl status clipmaster'
alias cm-logs='cd /home/ubuntu/clipmaster && docker-compose logs -f'
alias cm-update='cd /home/ubuntu/clipmaster && git pull && docker-compose build && docker-compose up -d'
alias cm-shell='cd /home/ubuntu/clipmaster && docker-compose exec api bash'
alias cm-db='cd /home/ubuntu/clipmaster && docker-compose exec postgres psql -U clipmaster -d clipmaster'
EOF

# Create update script
echo "📝 Creating update script..."
cat > /home/ubuntu/clipmaster/update.sh << 'EOF'
#!/bin/bash
echo "🔄 Updating ClipMaster..."
cd /home/ubuntu/clipmaster
git pull
docker-compose build
docker-compose up -d
echo "✅ ClipMaster updated and restarted"
EOF
chmod +x /home/ubuntu/clipmaster/update.sh

# Create backup script
echo "📝 Creating backup script..."
cat > /home/ubuntu/clipmaster/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/clipmaster-backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Creating ClipMaster backup..."
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U clipmaster clipmaster > $BACKUP_DIR/database_$DATE.sql

# Backup uploads (if not too large)
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz storage/uploads/

echo "✅ Backup created in $BACKUP_DIR"
echo "📁 Database: database_$DATE.sql"
echo "📁 Uploads: uploads_$DATE.tar.gz"
EOF
chmod +x /home/ubuntu/clipmaster/backup.sh

# Install monitoring script
echo "📝 Creating monitoring script..."
cat > /home/ubuntu/clipmaster/monitor.sh << 'EOF'
#!/bin/bash
echo "📊 ClipMaster System Status"
echo "=========================="
echo ""

echo "🐳 Docker Services:"
docker-compose ps

echo ""
echo "💾 Disk Usage:"
df -h /home/ubuntu/clipmaster/storage

echo ""
echo "🖥️  System Resources:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"

if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "🎮 GPU Status:"
    nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits
fi

echo ""
echo "📈 Storage Statistics:"
cd /home/ubuntu/clipmaster
docker-compose exec -T api python -c "
import asyncio
from app.core.database import database
from app.services.storage_service import StorageService

async def get_stats():
    await database.connect()
    storage_service = StorageService(database)
    info = await storage_service.get_storage_info()
    print(f'Videos: {info.video_count}')
    print(f'Clips: {info.clip_count}')
    print(f'Storage Usage: {info.usage_percentage:.1f}%')
    await database.disconnect()

asyncio.run(get_stats())
"
EOF
chmod +x /home/ubuntu/clipmaster/monitor.sh

echo ""
echo "🎉 ClipMaster installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /home/ubuntu/clipmaster/.env with your Twitch API credentials"
echo "2. Start ClipMaster: sudo systemctl start clipmaster"
echo "3. Access the application at http://localhost:3000"
echo "4. Monitor with: /home/ubuntu/clipmaster/monitor.sh"
echo ""
echo "🛠️  Useful commands:"
echo "• Start: cm-start"
echo "• Stop: cm-stop"
echo "• Restart: cm-restart"
echo "• View logs: cm-logs"
echo "• Update: ./update.sh"
echo "• Backup: ./backup.sh"
echo "• Monitor: ./monitor.sh"
echo ""
echo "⚠️  Note: You may need to log out and back in for Docker permissions to take effect"
echo ""
echo "🔧 If you encounter any issues, check the logs with: cm-logs"
