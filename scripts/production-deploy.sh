
#!/bin/bash

# ClipMaster Production Deployment Script
# Deploys ClipMaster for production use

set -e

echo "🚀 ClipMaster Production Deployment"
echo "===================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Prompt for domain name
read -p "🌐 Enter your domain name (e.g., clipmaster.example.com): " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    echo "❌ Domain name is required for production deployment"
    exit 1
fi

# Prompt for email for SSL certificate
read -p "📧 Enter your email for SSL certificate: " EMAIL

if [ -z "$EMAIL" ]; then
    echo "❌ Email is required for SSL certificate"
    exit 1
fi

# Generate production secrets
echo "🔐 Generating production secrets..."
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)

# Create production environment
echo "⚙️  Creating production environment..."
cat > .env.production << EOF
# Production Environment
NODE_ENV=production
DATABASE_URL=postgresql://clipmaster:${DB_PASSWORD}@postgres:5432/clipmaster
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# URLs
NEXT_PUBLIC_API_URL=https://${DOMAIN_NAME}
NEXTAUTH_URL=https://${DOMAIN_NAME}
ALLOWED_HOSTS=["https://${DOMAIN_NAME}"]
TWITCH_REDIRECT_URI=https://${DOMAIN_NAME}/twitch/callback

# Security
SECRET_KEY=${SECRET_KEY}
NEXTAUTH_SECRET=${SECRET_KEY}

# Storage
UPLOAD_DIR=/app/storage/uploads
CLIPS_DIR=/app/storage/clips
TEMP_DIR=/app/storage/temp
MAX_FILE_SIZE=5368709120

# AI Configuration
WHISPER_MODEL=base
WHISPER_DEVICE=cuda
ENABLE_GPU=true

# Production Settings
AUTO_CLEANUP_ENABLED=true
AUTO_CLEANUP_DAYS=30
AUTO_CLEANUP_THRESHOLD=0.8
LOG_LEVEL=INFO

# Twitch API (Update these!)
TWITCH_CLIENT_ID=your_production_client_id
TWITCH_CLIENT_SECRET=your_production_client_secret

# Database
POSTGRES_DB=clipmaster
POSTGRES_USER=clipmaster
POSTGRES_PASSWORD=${DB_PASSWORD}
EOF

# Copy production environment as main env
cp .env.production .env

echo "✅ Production environment created"

# Create production docker-compose
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: clipmaster_postgres_prod
    environment:
      POSTGRES_DB: clipmaster
      POSTGRES_USER: clipmaster
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - clipmaster_network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: clipmaster_redis_prod
    volumes:
      - redis_prod_data:/data
    networks:
      - clipmaster_network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    container_name: clipmaster_api_prod
    env_file: .env
    volumes:
      - ./storage:/app/storage
    depends_on:
      - postgres
      - redis
    networks:
      - clipmaster_network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: clipmaster_worker_prod
    env_file: .env
    volumes:
      - ./storage:/app/storage
    depends_on:
      - postgres
      - redis
    networks:
      - clipmaster_network
    restart: unless-stopped
    deploy:
      replicas: 2
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  ai_worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.ai_worker
    container_name: clipmaster_ai_worker_prod
    env_file: .env
    volumes:
      - ./storage:/app/storage
      - ./models:/app/models
    depends_on:
      - postgres
      - redis
    networks:
      - clipmaster_network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  beat:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: clipmaster_beat_prod
    command: celery -A app.tasks.celery_app beat --loglevel=info
    env_file: .env
    volumes:
      - ./storage:/app/storage
    depends_on:
      - postgres
      - redis
    networks:
      - clipmaster_network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build:
      context: ./app
      dockerfile: ../docker/Dockerfile.frontend
    container_name: clipmaster_frontend_prod
    environment:
      - NEXT_PUBLIC_API_URL=https://${DOMAIN_NAME}
      - NODE_ENV=production
    networks:
      - clipmaster_network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: clipmaster_nginx_prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./docker/ssl:/etc/nginx/ssl
      - ./storage/uploads:/var/www/uploads
      - certbot_certs:/etc/letsencrypt
      - certbot_webroot:/var/www/certbot
    depends_on:
      - api
      - frontend
    networks:
      - clipmaster_network
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  certbot:
    image: certbot/certbot
    container_name: clipmaster_certbot
    volumes:
      - certbot_certs:/etc/letsencrypt
      - certbot_webroot:/var/www/certbot
    command: certonly --webroot --webroot-path=/var/www/certbot --email ${EMAIL} --agree-tos --no-eff-email --staging -d ${DOMAIN_NAME}

volumes:
  postgres_prod_data:
  redis_prod_data:
  certbot_certs:
  certbot_webroot:

networks:
  clipmaster_network:
    driver: bridge
EOF

# Create production nginx config
cat > docker/nginx.prod.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }
    
    upstream api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=upload:10m rate=2r/s;

    # SSL Configuration
    server {
        listen 80;
        server_name ${DOMAIN_NAME};
        
        # ACME challenge
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Redirect HTTP to HTTPS
        location / {
            return 301 https://\$server_name\$request_uri;
        }
    }

    server {
        listen 443 ssl http2;
        server_name ${DOMAIN_NAME};
        
        # SSL certificates
        ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;
        
        # SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # Client max body size for file uploads
        client_max_body_size 5G;
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
        }
        
        # API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }
        
        # File uploads
        location /api/v1/videos/upload {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_read_timeout 600s;
            proxy_connect_timeout 75s;
            proxy_send_timeout 600s;
        }
        
        # Static files
        location /uploads/ {
            alias /var/www/uploads/;
            expires 1d;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

echo "🔧 Installing SSL certificate..."
# Start nginx temporarily for certificate
docker-compose -f docker-compose.prod.yml up -d nginx

# Get SSL certificate
docker-compose -f docker-compose.prod.yml run --rm certbot

echo "🚀 Starting production services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Create production management scripts
cat > start-prod.sh << EOF
#!/bin/bash
docker-compose -f docker-compose.prod.yml up -d
EOF

cat > stop-prod.sh << EOF
#!/bin/bash
docker-compose -f docker-compose.prod.yml down
EOF

cat > update-prod.sh << EOF
#!/bin/bash
echo "🔄 Updating ClipMaster production..."
docker-compose -f docker-compose.prod.yml down
git pull
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
echo "✅ Production updated"
EOF

chmod +x start-prod.sh stop-prod.sh update-prod.sh

# Set up SSL renewal cron job
(crontab -l 2>/dev/null; echo "0 12 * * * cd $(pwd) && docker-compose -f docker-compose.prod.yml run --rm certbot renew --quiet && docker-compose -f docker-compose.prod.yml restart nginx") | crontab -

echo ""
echo "🎉 Production deployment completed!"
echo ""
echo "🌐 Your ClipMaster instance is available at: https://${DOMAIN_NAME}"
echo ""
echo "⚠️  Important next steps:"
echo "1. Update Twitch API credentials in .env file"
echo "2. Configure your domain's DNS to point to this server"
echo "3. Test the application thoroughly"
echo ""
echo "🛠️  Production management:"
echo "• Start: ./start-prod.sh"
echo "• Stop: ./stop-prod.sh" 
echo "• Update: ./update-prod.sh"
echo "• Logs: docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🔒 Security:"
echo "• SSL certificate will auto-renew"
echo "• Change default passwords in .env"
echo "• Consider setting up monitoring and backups"
echo ""
echo "📊 Monitor your deployment:"
echo "• Server resources: htop"
echo "• Application logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "• SSL certificate: ./check-ssl.sh"
