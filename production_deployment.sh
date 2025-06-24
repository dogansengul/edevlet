#!/bin/bash

# 🏭 E-Devlet Automation Production Deployment Script
# Automates the complete production deployment process

set -e

# Configuration
PROJECT_NAME="edevlet-automation"
PROJECT_USER="edevlet"
PROJECT_DIR="/opt/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/edevlet"
BACKUP_DIR="/opt/backups/edevlet"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

create_user() {
    log "Creating system user: $PROJECT_USER"
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$PROJECT_DIR" "$PROJECT_USER"
        log "User $PROJECT_USER created"
    else
        log "User $PROJECT_USER already exists"
    fi
}

setup_directories() {
    log "Setting up directory structure"
    
    # Create main directories
    mkdir -p "$PROJECT_DIR" "$LOG_DIR" "$BACKUP_DIR"
    mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/downloads"
    
    # Set ownership
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    chown -R "$PROJECT_USER:$PROJECT_USER" "$LOG_DIR"
    
    # Set permissions
    chmod 750 "$PROJECT_DIR"
    chmod 755 "$LOG_DIR"
    chmod 700 "$BACKUP_DIR"
    
    log "Directory structure created"
}

install_system_dependencies() {
    log "Installing system dependencies"
    
    apt update
    apt install -y \
        nginx \
        python3 \
        python3-pip \
        python3-venv \
        sqlite3 \
        certbot \
        python3-certbot-nginx \
        ufw \
        logrotate \
        cron \
        curl \
        jq \
        htop \
        supervisor
    
    log "System dependencies installed"
}

setup_python_environment() {
    log "Setting up Python virtual environment"
    
    # Create virtual environment
    python3 -m venv "$VENV_DIR"
    chown -R "$PROJECT_USER:$PROJECT_USER" "$VENV_DIR"
    
    # Activate and install dependencies
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    
    # Install production dependencies
    pip install \
        gunicorn==21.2.0 \
        gevent==23.7.0 \
        psutil==5.9.5 \
        prometheus-client==0.17.1
    
    log "Python environment configured"
}

copy_application_files() {
    log "Copying application files"
    
    # Copy source files
    cp -r src/ "$PROJECT_DIR/"
    cp requirements.txt "$PROJECT_DIR/"
    cp wsgi.py "$PROJECT_DIR/"
    cp gunicorn.conf.py "$PROJECT_DIR/"
    cp run_event_system.py "$PROJECT_DIR/"
    
    # Install application dependencies
    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    pip install -r requirements.txt
    
    # Set ownership
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    log "Application files copied"
}

create_env_file() {
    log "Creating environment configuration"
    
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        cat > "$PROJECT_DIR/.env" << 'EOF'
# Production Environment Configuration
FLASK_ENV=production
LOG_LEVEL=INFO
SECRET_KEY=CHANGE_THIS_TO_A_SECURE_RANDOM_KEY_32_CHARS_MIN
BACKEND_API_BASE_URL=https://your-production-backend.com
BACKEND_API_EMAIL=production@yourdomain.com
BACKEND_API_PASSWORD=CHANGE_THIS_PASSWORD
ALLOWED_IPS=127.0.0.1,::1
PROCESSING_WAIT_INTERVAL_SECONDS=7200
EOF
        
        chmod 600 "$PROJECT_DIR/.env"
        chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR/.env"
        
        warn "Please edit $PROJECT_DIR/.env with your actual configuration values"
    else
        log "Environment file already exists"
    fi
}

setup_systemd_service() {
    log "Creating systemd service"
    
    cat > /etc/systemd/system/edevlet-automation.service << EOF
[Unit]
Description=E-Devlet Event-Driven Automation System
After=network.target
Requires=nginx.service

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PYTHONPATH=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn -c gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR/logs $PROJECT_DIR $LOG_DIR

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable edevlet-automation
    
    log "Systemd service created and enabled"
}

setup_nginx() {
    log "Configuring Nginx"
    
    # Copy nginx configuration
    cp nginx_proxy.conf /etc/nginx/sites-available/edevlet-app
    
    # Enable site
    ln -sf /etc/nginx/sites-available/edevlet-app /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t || error "Nginx configuration test failed"
    
    systemctl enable nginx
    systemctl reload nginx
    
    log "Nginx configured"
}

setup_firewall() {
    log "Configuring firewall"
    
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw --force enable
    
    log "Firewall configured"
}

setup_log_rotation() {
    log "Setting up log rotation"
    
    cat > /etc/logrotate.d/edevlet-automation << EOF
$LOG_DIR/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 644 $PROJECT_USER $PROJECT_USER
    postrotate
        systemctl reload edevlet-automation
    endscript
}

$PROJECT_DIR/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 644 $PROJECT_USER $PROJECT_USER
}
EOF

    log "Log rotation configured"
}

setup_backup_script() {
    log "Creating backup script"
    
    cat > /opt/backup_edevlet.sh << 'EOF'
#!/bin/bash
# E-Devlet Automation Backup Script

PROJECT_DIR="/opt/edevlet-automation"
BACKUP_DIR="/opt/backups/edevlet"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
if [[ -f "$PROJECT_DIR/queue.db" ]]; then
    sqlite3 "$PROJECT_DIR/queue.db" ".backup '$BACKUP_DIR/queue_$DATE.db'"
    gzip "$BACKUP_DIR/queue_$DATE.db"
    echo "Database backup completed: queue_$DATE.db.gz"
fi

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" -C /var/log edevlet/ 2>/dev/null || true
tar -czf "$BACKUP_DIR/app_logs_$DATE.tar.gz" -C "$PROJECT_DIR" logs/ 2>/dev/null || true

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed at $(date)"
EOF

    chmod +x /opt/backup_edevlet.sh
    
    # Add to crontab
    echo "0 2 * * * /opt/backup_edevlet.sh >> /var/log/backup.log 2>&1" | crontab -
    
    log "Backup script created and scheduled"
}

setup_monitoring() {
    log "Setting up basic monitoring"
    
    cat > /opt/health_check.sh << 'EOF'
#!/bin/bash
# Simple health check script

SERVICE_URL="http://127.0.0.1:5001/health"
LOG_FILE="/var/log/health_check.log"

# Check service health
if curl -f -s "$SERVICE_URL" > /dev/null; then
    echo "$(date): Service healthy" >> "$LOG_FILE"
else
    echo "$(date): Service unhealthy - attempting restart" >> "$LOG_FILE"
    systemctl restart edevlet-automation
fi

# Check disk space
DISK_USAGE=$(df / | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 }' | head -1 | cut -d'%' -f1)
if [[ $DISK_USAGE -gt 85 ]]; then
    echo "$(date): High disk usage: ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [[ $MEMORY_USAGE -gt 80 ]]; then
    echo "$(date): High memory usage: ${MEMORY_USAGE}%" >> "$LOG_FILE"
fi
EOF

    chmod +x /opt/health_check.sh
    
    # Add to crontab (every 5 minutes)
    echo "*/5 * * * * /opt/health_check.sh" | crontab -
    
    log "Basic monitoring configured"
}

finalize_deployment() {
    log "Finalizing deployment"
    
    # Set database permissions
    if [[ -f "$PROJECT_DIR/queue.db" ]]; then
        chmod 600 "$PROJECT_DIR/queue.db"
        chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR/queue.db"
    fi
    
    # Start services
    systemctl start edevlet-automation
    
    # Wait for service to start
    sleep 5
    
    # Check service status
    if systemctl is-active --quiet edevlet-automation; then
        log "✅ Service started successfully"
    else
        warn "⚠️ Service may have issues - check logs:"
        warn "journalctl -u edevlet-automation -f"
    fi
    
    log "🎉 Deployment completed successfully!"
}

main() {
    log "🚀 Starting E-Devlet Automation Production Deployment"
    
    check_root
    create_user
    setup_directories
    install_system_dependencies
    setup_python_environment
    copy_application_files
    create_env_file
    setup_systemd_service
    setup_nginx
    setup_firewall
    setup_log_rotation
    setup_backup_script
    setup_monitoring
    finalize_deployment
    
    echo ""
    echo "================================================================"
    echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "================================================================"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Edit $PROJECT_DIR/.env with your actual configuration"
    echo "2. Configure SSL certificate (run SSL setup script)"
    echo "3. Update ALLOWED_IPS in .env file"
    echo "4. Test the service:"
    echo "   curl http://localhost:5001/health"
    echo ""
    echo "📊 Management Commands:"
    echo "   systemctl status edevlet-automation   # Check status"
    echo "   systemctl restart edevlet-automation  # Restart service"
    echo "   journalctl -u edevlet-automation -f   # View logs"
    echo "   tail -f $LOG_DIR/gunicorn_access.log  # Access logs"
    echo ""
    echo "🔒 Security: Configure your backend IP in .env ALLOWED_IPS"
    echo "📁 Logs: $LOG_DIR/"
    echo "💾 Backups: $BACKUP_DIR/"
    echo ""
}

# Run main function
main "$@" 