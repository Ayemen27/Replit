#!/bin/bash
# =====================================================
# Production Server Setup Script
# AI Multi-Agent Server Automation System
# =====================================================

set -e  # Exit on error

echo "======================================================"
echo "AI Multi-Agent System - Production Setup"
echo "======================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_USER="${APP_USER:-aiagent}"
APP_DIR="${APP_DIR:-/srv/ai_system}"
PYTHON_VERSION="${PYTHON_VERSION:-3.9}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Main installation
main() {
    check_root
    
    log_info "Starting production setup..."
    echo ""
    
    # 1. System Update
    log_info "Updating system packages..."
    apt update
    apt upgrade -y
    log_info "✓ System updated"
    echo ""
    
    # 2. Install Python
    log_info "Installing Python ${PYTHON_VERSION}..."
    apt install -y python${PYTHON_VERSION} python3-pip python3-venv
    python3 --version
    log_info "✓ Python installed"
    echo ""
    
    # 3. Install PostgreSQL
    log_info "Installing PostgreSQL..."
    apt install -y postgresql postgresql-contrib
    systemctl start postgresql
    systemctl enable postgresql
    log_info "✓ PostgreSQL installed"
    echo ""
    
    # 4. Install system tools
    log_info "Installing system tools..."
    apt install -y git rsync curl wget htop ncdu fail2ban ufw
    log_info "✓ System tools installed"
    echo ""
    
    # 5. Create application user
    log_info "Creating application user: ${APP_USER}..."
    if ! id "${APP_USER}" &>/dev/null; then
        useradd -m -s /bin/bash ${APP_USER}
        log_info "✓ User ${APP_USER} created"
    else
        log_warn "User ${APP_USER} already exists"
    fi
    echo ""
    
    # 6. Create directories
    log_info "Creating application directories..."
    mkdir -p ${APP_DIR}/{releases,backups,logs}
    chown -R ${APP_USER}:${APP_USER} ${APP_DIR}
    chmod 755 ${APP_DIR}
    log_info "✓ Directories created"
    echo ""
    
    # 7. Setup SSH for app user
    log_info "Setting up SSH for ${APP_USER}..."
    mkdir -p /home/${APP_USER}/.ssh
    chmod 700 /home/${APP_USER}/.ssh
    touch /home/${APP_USER}/.ssh/authorized_keys
    chmod 600 /home/${APP_USER}/.ssh/authorized_keys
    chown -R ${APP_USER}:${APP_USER} /home/${APP_USER}/.ssh
    log_info "✓ SSH directory created"
    echo ""
    
    log_warn "Add your public SSH key to: /home/${APP_USER}/.ssh/authorized_keys"
    echo ""
    
    # 8. Setup PostgreSQL database
    log_info "Setting up PostgreSQL database..."
    sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '${APP_USER}') THEN
        CREATE USER ${APP_USER} WITH PASSWORD 'change_me_in_production';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE ai_system OWNER ${APP_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ai_system')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ai_system TO ${APP_USER};
EOF
    log_info "✓ Database setup complete"
    log_warn "IMPORTANT: Change database password in PostgreSQL!"
    echo ""
    
    # 9. Setup firewall
    log_info "Configuring firewall..."
    ufw --force enable
    ufw allow 22/tcp  # SSH
    ufw status
    log_info "✓ Firewall configured"
    echo ""
    
    # 10. Setup fail2ban
    log_info "Configuring fail2ban..."
    systemctl enable fail2ban
    systemctl start fail2ban
    log_info "✓ Fail2ban configured"
    echo ""
    
    # 11. Setup logrotate
    log_info "Setting up log rotation..."
    cat > /etc/logrotate.d/ai_agents <<'LOGROTATE'
/srv/ai_system/current/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 aiagent aiagent
    sharedscripts
    postrotate
        systemctl reload ai_agents >/dev/null 2>&1 || true
    endscript
}
LOGROTATE
    log_info "✓ Log rotation configured"
    echo ""
    
    # 12. Setup environment file
    log_info "Creating environment file template..."
    cat > ${APP_DIR}/.env.example <<'ENVFILE'
# PostgreSQL Configuration
PGHOST=localhost
PGPORT=5432
PGDATABASE=ai_system
PGUSER=aiagent
PGPASSWORD=change_me_in_production

# Telegram Notifications (Optional)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email Notifications (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
ENVFILE
    
    chown ${APP_USER}:${APP_USER} ${APP_DIR}/.env.example
    log_info "✓ Environment template created: ${APP_DIR}/.env.example"
    log_warn "Copy to .env and configure: cp ${APP_DIR}/.env.example ${APP_DIR}/.env"
    echo ""
    
    # 13. Create systemd service
    log_info "Creating systemd service..."
    cat > /etc/systemd/system/ai_agents.service <<SYSTEMD
[Unit]
Description=AI Multi-Agent Server Automation System
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}/current
EnvironmentFile=${APP_DIR}/.env

ExecStart=/usr/bin/python3 ${APP_DIR}/current/main.py start
ExecStop=/bin/kill -SIGTERM \$MAINPID

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai_agents

[Install]
WantedBy=multi-user.target
SYSTEMD
    
    systemctl daemon-reload
    log_info "✓ Systemd service created"
    echo ""
    
    # Summary
    echo "======================================================"
    log_info "Production setup completed successfully!"
    echo "======================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Add your SSH public key:"
    echo "   nano /home/${APP_USER}/.ssh/authorized_keys"
    echo ""
    echo "2. Configure environment variables:"
    echo "   cp ${APP_DIR}/.env.example ${APP_DIR}/.env"
    echo "   nano ${APP_DIR}/.env"
    echo ""
    echo "3. Change PostgreSQL password:"
    echo "   sudo -u postgres psql"
    echo "   ALTER USER ${APP_USER} WITH PASSWORD 'new_secure_password';"
    echo ""
    echo "4. Deploy the application:"
    echo "   # From your Replit environment:"
    echo "   python3 bridge_tool/cli.py init"
    echo "   python3 bridge_tool/cli.py test"
    echo "   python3 bridge_tool/cli.py push"
    echo ""
    echo "5. Enable and start the service:"
    echo "   sudo systemctl enable ai_agents"
    echo "   sudo systemctl start ai_agents"
    echo "   sudo systemctl status ai_agents"
    echo ""
    echo "======================================================"
}

# Run main function
main "$@"
