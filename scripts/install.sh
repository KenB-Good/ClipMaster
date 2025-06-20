#!/usr/bin/env bash

# ClipMaster Installation Script
# Cross-platform installation script for Ubuntu/Debian systems
# SECURITY: Fixed shell compatibility issues and hardcoded paths

set -e

echo "🎬 ClipMaster Installation Script"
echo "=================================="

# Detect OS and architecture
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VER=$DISTRIB_RELEASE
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    ARCH=$(uname -m)
    echo "📋 Detected OS: $OS $VER ($ARCH)"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        echo "❌ This script should not be run as root. Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    echo "🔍 Checking system requirements..."
    
    # Check if sudo is available
    if ! command -v sudo >/dev/null 2>&1; then
        echo "❌ sudo is required but not installed"
        exit 1
    fi
    
    # Check Ubuntu/Debian version compatibility
    case "$OS" in
        "Ubuntu")
            # SECURITY FIX: Use proper version comparison instead of string comparison
            MIN_VERSION="20.04"
            if [ "$(printf '%s\n' "$MIN_VERSION" "$VER" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
                echo "❌ Ubuntu 20.04 or higher is required (detected: $VER)"
                exit 1
            fi
            ;;
        "Debian GNU/Linux")
            MIN_VERSION="10"
            if [ "$(printf '%s\n' "$MIN_VERSION" "$VER" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
                echo "❌ Debian 10 or higher is required (detected: $VER)"
                exit 1
            fi
            ;;
        *)
            echo "⚠️  Unsupported OS: $OS. This script is designed for Ubuntu/Debian."
            echo "   Continuing anyway, but some features may not work correctly."
            ;;
    esac
    
    # Check available disk space (minimum 10GB)
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    MIN_SPACE=10485760  # 10GB in KB
    if [ "$AVAILABLE_SPACE" -lt "$MIN_SPACE" ]; then
        echo "❌ Insufficient disk space. At least 10GB required."
        exit 1
    fi
    
    echo "✅ System requirements met"
}

# Get user's home directory dynamically
get_user_home() {
    if [ -n "$CLIPMASTER_HOME" ]; then
        CLIPMASTER_DIR="$CLIPMASTER_HOME"
    elif [ -n "$CLIPMASTER_DIR" ]; then
        CLIPMASTER_DIR="$CLIPMASTER_DIR"
    else
        if [ -n "$HOME" ]; then
            USER_HOME="$HOME"
        else
            USER_HOME=$(getent passwd "$USER" | cut -d: -f6)
        fi

        if [ -z "$USER_HOME" ] || [ ! -d "$USER_HOME" ]; then
            echo "❌ Could not determine user home directory"
            exit 1
        fi

        CLIPMASTER_DIR="$USER_HOME/clipmaster"
    fi

    USER_HOME="${USER_HOME:-$(dirname "$CLIPMASTER_DIR")}" 
    echo "📁 ClipMaster will be installed to: $CLIPMASTER_DIR"
}

# Update system packages
update_system() {
    echo "📦 Updating system packages..."
    sudo apt update
    
    # Only upgrade if explicitly requested
    if [ "${UPGRADE_SYSTEM:-false}" = "true" ]; then
        sudo apt upgrade -y
    fi
}

# Install Docker with cross-platform support
install_docker() {
    echo "🐳 Installing Docker..."
    
    if command -v docker >/dev/null 2>&1; then
        echo "✅ Docker already installed"
        return
    fi
    
    # Install Docker using official script
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    
    # Add user to docker group
    sudo usermod -aG docker "$USER"
    
    # Clean up
    rm -f get-docker.sh
    
    echo "✅ Docker installed"
    echo "⚠️  You may need to log out and back in for Docker permissions to take effect"
}

# Install Docker Compose with architecture detection
install_docker_compose() {
    echo "🐳 Installing Docker Compose..."
    
    if command -v docker-compose >/dev/null 2>&1; then
        echo "✅ Docker Compose already installed"
        return
    fi
    
    # Map architecture names
    case "$ARCH" in
        "x86_64")
            COMPOSE_ARCH="x86_64"
            ;;
        "aarch64"|"arm64")
            COMPOSE_ARCH="aarch64"
            ;;
        "armv7l")
            COMPOSE_ARCH="armv7"
            ;;
        *)
            echo "❌ Unsupported architecture for Docker Compose: $ARCH"
            exit 1
            ;;
    esac
    
    # Get latest version
    COMPOSE_VERSION="v2.24.0"  # Use stable version
    COMPOSE_URL="https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-linux-${COMPOSE_ARCH}"
    
    sudo curl -L "$COMPOSE_URL" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker Compose installed"
}

# Install NVIDIA Docker support
install_nvidia_docker() {
    echo "🎮 Checking for NVIDIA GPU support..."
    
    if ! command -v nvidia-smi >/dev/null 2>&1; then
        echo "⚠️  No NVIDIA GPU detected, skipping NVIDIA Docker installation"
        return
    fi
    
    echo "🎮 NVIDIA GPU detected, installing NVIDIA Docker..."
    
    # Add NVIDIA Docker repository
    distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L "https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list" | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    sudo apt update
    sudo apt install -y nvidia-container-toolkit
    sudo systemctl restart docker
    
    echo "✅ NVIDIA Docker installed"
}

# Install system dependencies
install_dependencies() {
    echo "📦 Installing system dependencies..."
    
    # Essential packages
    PACKAGES="curl git wget unzip htop tree jq ffmpeg python3-pip"
    
    # Add Node.js repository and install
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    PACKAGES="$PACKAGES nodejs"
    
    # Install packages
    sudo apt install -y $PACKAGES
    
    # Install Yarn
    if ! command -v yarn >/dev/null 2>&1; then
        echo "📦 Installing Yarn..."
        curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/yarn-keyring.gpg
        echo "deb [signed-by=/usr/share/keyrings/yarn-keyring.gpg] https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
        sudo apt update && sudo apt install -y yarn
        echo "✅ Yarn installed"
    else
        echo "✅ Yarn already installed"
    fi
    
    echo "✅ System dependencies installed"
}

# Create directory structure
create_directories() {
    echo "📁 Creating directory structure..."
    
    # Create main directories
    mkdir -p "$CLIPMASTER_DIR"/{storage/{uploads,clips,temp},models,logs,backups}
    
    # Set proper permissions
    chmod 755 "$CLIPMASTER_DIR"
    chmod 755 "$CLIPMASTER_DIR"/storage
    chmod 777 "$CLIPMASTER_DIR"/storage/{uploads,clips,temp}  # Writable by Docker containers
    
    echo "✅ Directory structure created"
}

# Set up environment configuration
setup_environment() {
    echo "⚙️  Setting up environment configuration..."
    
    # Generate secure random keys
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | base64 | tr -d '\n')
    NEXTAUTH_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | base64 | tr -d '\n')
    DB_PASSWORD=$(openssl rand -hex 16 2>/dev/null || head -c 16 /dev/urandom | base64 | tr -d '\n')
    
    # Create environment file
    cat > "$CLIPMASTER_DIR/.env" << EOF
# ClipMaster Environment Configuration
# Generated on $(date)

# Database
DATABASE_URL=postgresql://clipmaster:${DB_PASSWORD}@localhost:5432/clipmaster
POSTGRES_DB=clipmaster
POSTGRES_USER=clipmaster
POSTGRES_PASSWORD=${DB_PASSWORD}

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Storage (using dynamic paths)
UPLOAD_DIR=${CLIPMASTER_DIR}/storage/uploads
CLIPS_DIR=${CLIPMASTER_DIR}/storage/clips
TEMP_DIR=${CLIPMASTER_DIR}/storage/temp

# AI Models
WHISPER_MODEL=base
WHISPER_DEVICE=$(command -v nvidia-smi >/dev/null 2>&1 && echo "cuda" || echo "cpu")
ENABLE_GPU=$(command -v nvidia-smi >/dev/null 2>&1 && echo "true" || echo "false")

# Twitch API (Configure these with your Twitch app credentials)
TWITCH_CLIENT_ID=your_twitch_client_id_here
TWITCH_CLIENT_SECRET=your_twitch_client_secret_here
TWITCH_REDIRECT_URI=http://localhost:3000/twitch/callback

# Security (auto-generated secure keys)
SECRET_KEY=${SECRET_KEY}
NEXTAUTH_SECRET=${NEXTAUTH_SECRET}

# API Configuration
ALLOWED_HOSTS=["http://localhost:3000", "http://127.0.0.1:3000"]
NEXT_PUBLIC_API_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO

# Development
NODE_ENV=production
DEBUG=false
EOF
    
    # Set secure permissions on .env file
    chmod 600 "$CLIPMASTER_DIR/.env"
    
    echo "✅ Environment file created at $CLIPMASTER_DIR/.env"
    echo "⚠️  Please update the Twitch API credentials in the .env file"
}

# Set up systemd service
setup_systemd_service() {
    echo "⚙️  Setting up systemd service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/clipmaster.service > /dev/null << EOF
[Unit]
Description=ClipMaster AI Video Processing System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${CLIPMASTER_DIR}
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=${USER}
Group=docker
Environment=HOME=${USER_HOME}

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable clipmaster
    
    echo "✅ ClipMaster systemd service installed"
}

# Install additional utilities
install_utilities() {
    echo "🛠️  Installing additional utilities..."
    
    # Install btop (better htop) if available
    if [ "$ARCH" = "x86_64" ]; then
        if ! command -v btop >/dev/null 2>&1; then
            BTOP_URL="https://github.com/aristocratos/btop/releases/latest/download/btop-x86_64-linux-musl.tbz"
            wget -q "$BTOP_URL" -O btop.tbz
            tar -xjf btop.tbz
            sudo cp btop/bin/btop /usr/local/bin/
            rm -rf btop btop.tbz
            echo "✅ btop installed"
        fi
    fi
    
    # Install NVIDIA monitoring tools if GPU present
    if command -v nvidia-smi >/dev/null 2>&1; then
        pip3 install --user nvidia-ml-py3
        echo "✅ NVIDIA monitoring tools installed"
    fi
}

# Set up useful aliases and scripts
setup_aliases() {
    echo "⚙️  Setting up useful aliases and scripts..."
    
    # Add aliases to bashrc
    cat >> "$USER_HOME/.bashrc" << EOF

# ClipMaster aliases (added by installer)
alias cm-start='cd ${CLIPMASTER_DIR} && sudo systemctl start clipmaster'
alias cm-stop='cd ${CLIPMASTER_DIR} && sudo systemctl stop clipmaster'
alias cm-restart='cd ${CLIPMASTER_DIR} && sudo systemctl restart clipmaster'
alias cm-status='cd ${CLIPMASTER_DIR} && sudo systemctl status clipmaster'
alias cm-logs='cd ${CLIPMASTER_DIR} && docker-compose logs -f'
alias cm-update='cd ${CLIPMASTER_DIR} && git pull && docker-compose build && docker-compose up -d'
alias cm-shell='cd ${CLIPMASTER_DIR} && docker-compose exec api bash'
alias cm-db='cd ${CLIPMASTER_DIR} && docker-compose exec postgres psql -U clipmaster -d clipmaster'
EOF
    
    # Create utility scripts
    create_utility_scripts
}

# Create utility scripts
create_utility_scripts() {
    # Update script
    cat > "$CLIPMASTER_DIR/update.sh" << 'EOF'
#!/usr/bin/env bash
set -e
echo "🔄 Updating ClipMaster..."
cd "$(dirname "$0")"
git pull
docker-compose build
docker-compose up -d
echo "✅ ClipMaster updated and restarted"
EOF
    
    # Backup script
    cat > "$CLIPMASTER_DIR/backup.sh" << EOF
#!/usr/bin/env bash
set -e
BACKUP_DIR="${CLIPMASTER_DIR}/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

echo "💾 Creating ClipMaster backup..."
mkdir -p "\$BACKUP_DIR"

cd "${CLIPMASTER_DIR}"

# Backup database
if docker-compose ps postgres | grep -q "Up"; then
    docker-compose exec -T postgres pg_dump -U clipmaster clipmaster > "\$BACKUP_DIR/database_\$DATE.sql"
    echo "✅ Database backed up"
else
    echo "⚠️  Database container not running, skipping database backup"
fi

# Backup uploads (if not too large)
if [ -d "storage/uploads" ] && [ "\$(du -s storage/uploads | cut -f1)" -lt 1048576 ]; then
    tar -czf "\$BACKUP_DIR/uploads_\$DATE.tar.gz" storage/uploads/
    echo "✅ Uploads backed up"
else
    echo "⚠️  Uploads directory too large or missing, skipping uploads backup"
fi

echo "✅ Backup completed in \$BACKUP_DIR"
EOF
    
    # Monitor script
    cat > "$CLIPMASTER_DIR/monitor.sh" << EOF
#!/usr/bin/env bash
echo "📊 ClipMaster System Status"
echo "=========================="
echo ""

cd "${CLIPMASTER_DIR}"

echo "🐳 Docker Services:"
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose ps
else
    echo "Docker Compose not available"
fi

echo ""
echo "💾 Disk Usage:"
df -h "${CLIPMASTER_DIR}/storage" 2>/dev/null || df -h "${CLIPMASTER_DIR}"

echo ""
echo "🖥️  System Resources:"
if command -v top >/dev/null 2>&1; then
    CPU_USAGE=\$(top -bn1 | grep "Cpu(s)" | awk '{print \$2}' | cut -d'%' -f1 2>/dev/null || echo "N/A")
    echo "CPU: \${CPU_USAGE}%"
fi

if command -v free >/dev/null 2>&1; then
    MEM_USAGE=\$(free | grep Mem | awk '{printf("%.1f%%", \$3/\$2 * 100.0)}' 2>/dev/null || echo "N/A")
    echo "Memory: \$MEM_USAGE"
fi

if command -v nvidia-smi >/dev/null 2>&1; then
    echo ""
    echo "🎮 GPU Status:"
    nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null || echo "GPU info unavailable"
fi
EOF
    
    # Make scripts executable
    chmod +x "$CLIPMASTER_DIR"/{update.sh,backup.sh,monitor.sh}
    
    echo "✅ Utility scripts created"
}

# Main installation function
main() {
    echo "Starting ClipMaster installation..."
    
    detect_os
    check_root
    check_requirements
    get_user_home
    
    update_system
    install_docker
    install_docker_compose
    install_nvidia_docker
    install_dependencies
    
    create_directories
    setup_environment
    setup_systemd_service
    install_utilities
    setup_aliases
    
    echo ""
    echo "🎉 ClipMaster installation completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit $CLIPMASTER_DIR/.env with your Twitch API credentials"
    echo "2. Start ClipMaster: sudo systemctl start clipmaster"
    echo "3. Access the application at http://localhost:3000"
    echo "4. Monitor with: $CLIPMASTER_DIR/monitor.sh"
    echo ""
    echo "🛠️  Useful commands:"
    echo "• Start: cm-start"
    echo "• Stop: cm-stop"
    echo "• Restart: cm-restart"
    echo "• View logs: cm-logs"
    echo "• Update: $CLIPMASTER_DIR/update.sh"
    echo "• Backup: $CLIPMASTER_DIR/backup.sh"
    echo "• Monitor: $CLIPMASTER_DIR/monitor.sh"
    echo ""
    echo "⚠️  Note: You may need to log out and back in for Docker permissions to take effect"
    echo ""
    echo "🔧 If you encounter any issues, check the logs with: cm-logs"
}

# Run main function
main "$@"