
# 🎬 ClipMaster - AI-Powered Video Clipping System

ClipMaster is a comprehensive AI-powered video processing system that automatically detects highlights, generates clips, and provides real-time Twitch stream monitoring with intelligent highlight detection.

## ✨ Features

### 🤖 AI-Powered Processing
- **Whisper Integration**: Speech-to-text transcription with multiple language support
- **Highlight Detection**: Multi-modal analysis using audio spikes, scene changes, and text patterns
- **Custom Prompts**: User-defined highlight criteria using natural language
- **"Clip That" Detection**: Automatic detection of exciting moments in speech and chat
- **Emotional Reaction Detection**: Audio spike analysis for emotional moments

### 🎮 Twitch Integration
- **Live Stream Monitoring**: Real-time stream capture and analysis
- **Chat Analysis**: Intelligent chat monitoring for excitement detection
- **Auto-Clipping**: Automatic clip creation during live streams
- **VOD Processing**: Process Twitch VODs for highlight extraction
- **Multiple Channel Support**: Monitor multiple streamers simultaneously

### 🎥 Video Processing
- **Multiple Format Support**: Process various video formats
- **Clip Generation**: Automatic clip creation with customizable duration
- **Subtitle Generation**: Automatic subtitle creation and overlay
- **Format Optimization**: Convert clips for different platforms (TikTok, YouTube, Instagram)
- **Batch Processing**: Process multiple videos simultaneously

### 📊 Management & Monitoring
- **Web Dashboard**: Modern React-based interface
- **Storage Management**: Automatic cleanup and space monitoring
- **Task Queue System**: Background processing with progress tracking
- **Real-time Updates**: WebSocket-based status updates
- **Performance Monitoring**: System resource and GPU monitoring

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04 or higher
- 16GB+ RAM (32GB+ recommended for AI processing)
- NVIDIA GPU (optional but recommended for faster processing)
- 100GB+ free disk space
- Docker and Docker Compose

### One-Click Installation

```bash
# Clone the repository
git clone https://github.com/your-username/clipmaster.git
cd clipmaster

# Run the installation script
chmod +x scripts/install.sh
./scripts/install.sh

# Set up environment
chmod +x scripts/setup-env.sh
./scripts/setup-env.sh

# Start ClipMaster
docker-compose up -d
```

### Manual Installation

1. **Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# For GPU support (if NVIDIA GPU available)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-docker2
sudo systemctl restart docker
```

2. **Configure Environment**
```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Update Twitch API credentials
TWITCH_CLIENT_ID=your_client_id
TWITCH_CLIENT_SECRET=your_client_secret
```

3. **Start Services**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WHISPER_MODEL` | Whisper model size (tiny, base, small, medium, large) | `base` |
| `WHISPER_DEVICE` | Processing device (cpu, cuda) | `cuda` |
| `ENABLE_GPU` | Enable GPU acceleration | `true` |
| `CONFIDENCE_THRESHOLD` | Minimum confidence for highlights | `0.7` |
| `AUTO_CLEANUP_ENABLED` | Enable automatic file cleanup | `true` |
| `AUTO_CLEANUP_DAYS` | Days before files are eligible for cleanup | `30` |
| `MAX_FILE_SIZE` | Maximum upload file size in bytes | `5368709120` (5GB) |

### Twitch API Setup

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Create a new application
3. Set redirect URI to `http://localhost:3000/twitch/callback`
4. Copy Client ID and Client Secret to your `.env` file

### Custom Prompts

Create custom highlight detection prompts in the web interface:

```
Find moments with intense gameplay, skillful plays, or exciting reactions
Identify funny moments, jokes, laughter, and comedic situations  
Detect strong emotional reactions, excitement, surprise, or dramatic moments
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Server    │    │   AI Workers    │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   PostgreSQL    │    │   Redis         │
│   (Proxy)       │    │   (Database)    │    │   (Queue)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Services

- **Frontend**: Next.js React application with modern UI
- **API**: FastAPI backend with async support
- **AI Workers**: Celery workers for video processing with GPU support
- **Database**: PostgreSQL for data persistence
- **Queue**: Redis for task queuing and caching
- **Proxy**: Nginx for load balancing and static file serving

## 📱 Usage

### Web Interface

1. **Upload Videos**: Drag and drop videos for processing
2. **Monitor Progress**: Real-time processing status updates
3. **Browse Highlights**: View detected highlights with confidence scores
4. **Download Clips**: Generated clips in multiple formats
5. **Twitch Integration**: Connect and monitor Twitch streams
6. **Custom Prompts**: Create and manage custom highlight criteria

### API Endpoints

```bash
# Upload video
curl -X POST http://localhost:8000/api/v1/videos/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@video.mp4"

# Get video status
curl http://localhost:8000/api/v1/videos/{video_id}

# Get highlights
curl http://localhost:8000/api/v1/videos/{video_id}/highlights

# Start Twitch monitoring
curl -X POST http://localhost:8000/api/v1/twitch/{integration_id}/start-monitoring
```

### CLI Commands

```bash
# ClipMaster management
cm-start          # Start services
cm-stop           # Stop services  
cm-restart        # Restart services
cm-status         # Check status
cm-logs           # View logs
cm-update         # Update and restart

# System monitoring
./monitor.sh      # System status
./backup.sh       # Create backup
./update.sh       # Update ClipMaster
```

## 🔧 Advanced Configuration

### GPU Optimization

For multiple GPUs:
```yaml
# docker-compose.yml
ai_worker:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            device_ids: ['0', '1']  # Specific GPU IDs
            capabilities: [gpu]
```

### Production Deployment

1. **SSL Configuration**
```bash
# Generate SSL certificates
sudo certbot --nginx -d your-domain.com

# Update nginx configuration
# Edit docker/nginx.conf for SSL
```

2. **Environment Configuration**
```bash
# Use production environment
cp .env.production .env
# Update with production values
```

3. **Resource Scaling**
```yaml
# Scale workers
docker-compose up -d --scale worker=3 --scale ai_worker=2
```

### Custom Model Configuration

```bash
# Use larger Whisper model for better accuracy
WHISPER_MODEL=large

# Custom model cache directory
TORCH_HOME=/custom/model/path
```

## 📊 Monitoring

### System Status
```bash
# Service status
docker-compose ps

# Resource usage
./monitor.sh

# GPU monitoring (if available)
nvidia-smi

# Celery task monitoring
# Access Flower at http://localhost:5555
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f ai_worker

# Database logs
docker-compose logs -f postgres
```

### Metrics
- Processing times and success rates
- Storage usage and cleanup statistics  
- GPU utilization and memory usage
- API response times and error rates

## 🛠️ Troubleshooting

### Common Issues

**GPU Not Detected**
```bash
# Check NVIDIA drivers
nvidia-smi

# Verify Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi
```

**Out of Memory Errors**
```bash
# Reduce worker concurrency
# Edit docker-compose.yml
command: celery -A app.tasks.celery_app worker --concurrency=1

# Use smaller Whisper model
WHISPER_MODEL=tiny
```

**Database Connection Issues**
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait for database to be ready
docker-compose up -d
```

**Storage Issues**
```bash
# Clean up storage
docker-compose exec api python -c "
from app.services.storage_service import StorageService
from app.core.database import database
import asyncio
async def cleanup():
    await database.connect()
    service = StorageService(database)
    result = await service.cleanup_storage(force=True)
    print(result)
    await database.disconnect()
asyncio.run(cleanup())
"
```

### Performance Optimization

1. **Increase worker processes** for more parallel processing
2. **Use SSD storage** for faster I/O operations
3. **Add more RAM** for larger video processing
4. **Use multiple GPUs** for AI processing acceleration
5. **Optimize database** with proper indexing and connection pooling

## 🔒 Security

### Production Security Checklist

- [ ] Change default passwords and secrets
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Enable log monitoring
- [ ] Configure rate limiting
- [ ] Set up authentication
- [ ] Secure API endpoints

### Backup Strategy

```bash
# Automated backup
./backup.sh

# Manual database backup
docker-compose exec postgres pg_dump -U clipmaster clipmaster > backup.sql

# Manual file backup
tar -czf storage_backup.tar.gz storage/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/clipmaster/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/clipmaster/discussions)

## 🎯 Roadmap

- [ ] Real-time streaming integration
- [ ] Advanced AI models for better highlight detection
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Cloud deployment options
- [ ] Advanced analytics and reporting
- [ ] Integration with more streaming platforms

---

**ClipMaster** - Transform your content with AI-powered video processing! 🎬✨
