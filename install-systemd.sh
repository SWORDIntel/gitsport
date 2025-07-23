#!/bin/bash
# GitLab Export - Systemd Service Installation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}GitLab Export - Systemd Service Installer${NC}"
echo "=========================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}" 
   exit 1
fi

# Default values
INSTALL_DIR="/opt/gitlab-export"
SERVICE_USER="gitlab-export"
SYSTEMD_DIR="/etc/systemd/system"

# Check if service files exist locally
if [[ ! -f "gitlab-export.service" ]] || [[ ! -f "gitlab-export.timer" ]]; then
    echo -e "${YELLOW}Creating systemd service files...${NC}"
    
    # Create service file
    cat > gitlab-export.service << 'EOF'
[Unit]
Description=GitLab Project Export Service
Documentation=https://gitlab.com/
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=gitlab-export
Group=gitlab-export
WorkingDirectory=/opt/gitlab-export
Environment="PATH=/opt/gitlab-export/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/gitlab-export/venv/bin/python /opt/gitlab-export/gitlab_async_tui_exporter.py
TimeoutStartSec=0
TimeoutStopSec=14400
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/gitlab-export/exports /opt/gitlab-export/logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gitlab-export
Restart=on-failure
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

    # Create timer file
    cat > gitlab-export.timer << 'EOF'
[Unit]
Description=GitLab Export Timer - Daily at 2 AM
Requires=gitlab-export.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true
RandomizedDelaySec=3600
ConditionACPower=true

[Install]
WantedBy=timers.target
EOF
    
    echo -e "${GREEN}✓ Created service files${NC}"
fi

# Create system user if doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${YELLOW}Creating system user: $SERVICE_USER${NC}"
    useradd -r -m -d "$INSTALL_DIR" -s /bin/bash "$SERVICE_USER"
    echo -e "${GREEN}✓ User created${NC}"
else
    echo -e "${GREEN}✓ User $SERVICE_USER already exists${NC}"
fi

# Create installation directory
if [[ ! -d "$INSTALL_DIR" ]]; then
    echo -e "${YELLOW}Creating installation directory: $INSTALL_DIR${NC}"
    mkdir -p "$INSTALL_DIR"
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    echo -e "${GREEN}✓ Directory created${NC}"
fi

# Copy current files to installation directory
echo -e "${YELLOW}Copying application files...${NC}"
FILES_TO_COPY=(
    "gitlab_async_tui_exporter.py"
    "requirements-async.txt"
    "gitlab_instances.txt"
    "convert_config.py"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [[ -f "$file" ]]; then
        cp "$file" "$INSTALL_DIR/"
        chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/$file"
        echo -e "  ✓ Copied $file"
    else
        echo -e "  ${YELLOW}⚠ $file not found, skipping${NC}"
    fi
done

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
sudo -u "$SERVICE_USER" mkdir -p "$INSTALL_DIR/exports" "$INSTALL_DIR/logs"
echo -e "${GREEN}✓ Directories created${NC}"

# Install systemd files
echo -e "${YELLOW}Installing systemd files...${NC}"
cp gitlab-export.service "$SYSTEMD_DIR/"
cp gitlab-export.timer "$SYSTEMD_DIR/"
echo -e "${GREEN}✓ Systemd files installed${NC}"

# Set up Python environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
if [[ ! -d "$INSTALL_DIR/venv" ]]; then
    sudo -u "$SERVICE_USER" python3 -m venv "$INSTALL_DIR/venv"
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements-async.txt"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Reload systemd
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
systemctl daemon-reload
echo -e "${GREEN}✓ Systemd reloaded${NC}"

# Show status
echo
echo -e "${GREEN}Installation Complete!${NC}"
echo "====================="
echo
echo "Next steps:"
echo "1. Configure your GitLab instances:"
echo "   sudo -u $SERVICE_USER nano $INSTALL_DIR/gitlab_instances.txt"
echo
echo "2. Test the service manually:"
echo "   sudo systemctl start gitlab-export.service"
echo "   sudo journalctl -u gitlab-export.service -f"
echo
echo "3. Enable the timer for automatic exports:"
echo "   sudo systemctl enable --now gitlab-export.timer"
echo
echo "4. Check timer status:"
echo "   systemctl status gitlab-export.timer"
echo "   systemctl list-timers gitlab-export.timer"
echo
echo -e "${GREEN}Service will run daily at 2:00 AM${NC}"
echo "To change schedule, edit: $SYSTEMD_DIR/gitlab-export.timer"
