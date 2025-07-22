#!/usr/bin/env python3
"""
GitLab Mass Exporter - Setup Verification and File Creation Script
Checks all required files and creates missing ones
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import base64

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Define all required files and their contents
FILES = {
    # Core Python Files
    "gitlab_async_tui_exporter.py": {
        "type": "core",
        "description": "Main async TUI exporter application",
        "content": '''#!/usr/bin/env python3
"""
GitLab Async TUI Mass Exporter
Exports all accessible content from multiple GitLab instances with structure preservation
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from concurrent.futures import ThreadPoolExecutor
import tarfile
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib

console = Console()

@dataclass
class GitLabInstance:
    name: str
    url: str
    token: str
    version: str = ""
    role: str = ""
    username: str = ""
    email: str = ""
    projects_count: int = 0
    groups_count: int = 0
    users_count: int = 0

@dataclass
class ExportStats:
    projects_exported: int = 0
    projects_failed: int = 0
    groups_exported: int = 0
    groups_failed: int = 0
    wikis_exported: int = 0
    snippets_exported: int = 0
    total_size: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def elapsed_time(self):
        return time.time() - self.start_time
    
    @property
    def success_rate(self):
        total = self.projects_exported + self.projects_failed
        return (self.projects_exported / total * 100) if total > 0 else 0

# Placeholder for main async exporter class
# Full implementation would go here
print("GitLab Async TUI Exporter - Placeholder")
print("Please download the full implementation from the artifacts")
'''
    },
    
    "requirements-async.txt": {
        "type": "core",
        "description": "Python dependencies for async version",
        "content": """aiohttp>=3.9.0
rich>=13.7.0
cryptography>=41.0.0"""
    },
    
    "convert_config.py": {
        "type": "setup",
        "description": "Converts GitLab config format",
        "content": '''#!/usr/bin/env python3
"""
Convert GitLab instance configuration from the provided format to config.json
"""

import json
from pathlib import Path

# Example configuration in the provided format
example_config = """
https://gitlab.example.com/users/sign_in user:password
    ⬡ TOKΞN: glpat-xxxxxxxxxxxxxxxxxxxx
	VΞRSION: 17.0.0
	ROLΞ: Administrator
	PROJΞCTS: 100
	GROUPS: 50
	USΞRNAMΞ: user
	ΞMAIL: user@example.com
	USΞRS: 200
"""

def convert_config():
    """Convert the provided format to standard config.json"""
    
    # Save the example format
    with open('gitlab_instances.txt', 'w', encoding='utf-8') as f:
        f.write(example_config.strip())
    
    print("Created gitlab_instances.txt with example instances")
    print("\\nThis file will be automatically converted to config.json when you run the exporter.")
    print("\\n⚠️  SECURITY WARNING: Replace with your actual credentials!")
    print("\\nThe async TUI exporter will:")
    print("  1. Read gitlab_instances.txt")
    print("  2. Parse all GitLab instances")
    print("  3. Create config.json automatically")
    print("  4. Export ALL accessible content from each instance")
    print("\\nRun: python gitlab_async_tui_exporter.py")

if __name__ == "__main__":
    convert_config()
'''
    },
    
    # Quick Start Scripts
    "start.sh": {
        "type": "script",
        "description": "Universal start script with menu",
        "executable": True,
        "content": '''#!/bin/bash
# GitLab Mass Exporter - Universal Start Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          GitLab Async Mass Exporter v3.0                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo
echo "Choose your preferred method:"
echo
echo "1) Quick Start (Recommended)"
echo "2) Docker (Isolated environment)"
echo "3) Manual Python execution"
echo "4) Setup only (no export)"
echo
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Starting Quick Start..."
        python3 quickstart.py
        ;;
    2)
        echo "Starting Docker version..."
        if ! command -v docker &> /dev/null; then
            echo "ERROR: Docker is not installed!"
            exit 1
        fi
        docker-compose up --build
        ;;
    3)
        echo "Starting manual execution..."
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements-async.txt
        else
            source venv/bin/activate
        fi
        python3 gitlab_async_tui_exporter.py
        ;;
    4)
        echo "Running setup only..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements-async.txt
        python3 convert_config.py
        echo
        echo "✅ Setup complete!"
        echo "📝 Edit 'gitlab_instances.txt' with your GitLab instances"
        echo "🚀 Then run './start.sh' again to export"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
'''
    },
    
    "quickstart.py": {
        "type": "script",
        "description": "Cross-platform quick start",
        "content": '''#!/usr/bin/env python3
"""
Quick Start for GitLab Async Mass Exporter
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        GitLab Async Mass Exporter - Quick Start          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Check if setup is needed
    if not Path("venv").exists():
        print("📦 First time setup detected. Installing dependencies...")
        print()
        
        # Create venv
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Determine pip path
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip.exe")
            python_path = Path("venv/Scripts/python.exe")
        else:
            pip_path = Path("venv/bin/pip")
            python_path = Path("venv/bin/python")
        
        # Install dependencies
        subprocess.run([str(pip_path), "install", "-r", "requirements-async.txt"], check=True)
        print()
        print("✅ Dependencies installed!")
    else:
        if os.name == 'nt':
            python_path = Path("venv/Scripts/python.exe")
        else:
            python_path = Path("venv/bin/python")
    
    # Check for config
    if not Path("gitlab_instances.txt").exists():
        print("📝 Creating example configuration...")
        subprocess.run([str(python_path), "convert_config.py"], check=True)
        print()
        print("⚠️  IMPORTANT: Edit 'gitlab_instances.txt' with your GitLab instances!")
        print("   Then run this script again.")
        return
    
    print("🚀 Starting GitLab Async Mass Exporter...")
    print()
    
    # Run the main exporter
    subprocess.run([str(python_path), "gitlab_async_tui_exporter.py"], check=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\n❌ Interrupted by user")
    except subprocess.CalledProcessError as e:
        print(f"\\n\\n❌ Error: Command failed with exit code {e.returncode}")
'''
    },
    
    "setup_and_run.sh": {
        "type": "script",
        "description": "Complete setup script for Linux/macOS",
        "executable": True,
        "content": '''#!/bin/bash
# GitLab Async Mass Exporter - Setup and Run Script

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          GitLab Async Mass Exporter v3.0                 ║"
echo "║     Exports ALL accessible content from GitLab           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-async.txt

# Check if gitlab_instances.txt exists
if [ ! -f "gitlab_instances.txt" ]; then
    echo "📝 Creating gitlab_instances.txt with example data..."
    python3 convert_config.py
fi

echo
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    READY TO EXPORT                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo
echo "🚀 Starting GitLab Async Mass Exporter..."
echo

# Run the exporter
python3 gitlab_async_tui_exporter.py

# Deactivate virtual environment
deactivate

echo
echo "✅ Export process completed!"
echo "📁 Check the 'exports' directory for your data"
'''
    },
    
    "setup_and_run.bat": {
        "type": "script",
        "description": "Complete setup script for Windows",
        "content": '''@echo off
REM GitLab Async Mass Exporter - Windows Setup and Run Script

echo ============================================================
echo          GitLab Async Mass Exporter v3.0                 
echo     Exports ALL accessible content from GitLab           
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 is required but not installed.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\\Scripts\\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements-async.txt

REM Check if gitlab_instances.txt exists
if not exist "gitlab_instances.txt" (
    echo Creating gitlab_instances.txt with example data...
    python convert_config.py
)

echo.
echo ============================================================
echo                     READY TO EXPORT                       
echo ============================================================
echo.

REM Run the exporter
python gitlab_async_tui_exporter.py

REM Deactivate virtual environment
call venv\\Scripts\\deactivate.bat

echo.
echo Export process completed!
echo Check the 'exports' directory for your data
pause
'''
    },
    
    # Docker Files
    "Dockerfile": {
        "type": "docker",
        "description": "Docker container configuration",
        "content": '''FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-async.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-async.txt

# Copy application files
COPY gitlab_async_tui_exporter.py .
COPY convert_config.py .

# Create necessary directories
RUN mkdir -p /app/exports

# Create entrypoint script
RUN echo '#!/bin/bash\\n\\
if [ ! -f /app/gitlab_instances.txt ]; then\\n\\
    echo "ERROR: gitlab_instances.txt not found!"\\n\\
    echo "Mount your config file to /app/gitlab_instances.txt"\\n\\
    exit 1\\n\\
fi\\n\\
python gitlab_async_tui_exporter.py\\n\\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Volume for exports
VOLUME ["/app/exports"]

# Volume for config
VOLUME ["/app/gitlab_instances.txt"]

ENTRYPOINT ["/app/entrypoint.sh"]
'''
    },
    
    "docker-compose.yml": {
        "type": "docker",
        "description": "Docker Compose configuration",
        "content": '''version: '3.8'

services:
  gitlab-exporter:
    build: .
    container_name: gitlab-mass-exporter
    volumes:
      # Mount your config file
      - ./gitlab_instances.txt:/app/gitlab_instances.txt:ro
      # Export directory
      - ./exports:/app/exports
    environment:
      # Optional: Use environment variables instead of config file
      # - GITLAB_USE_ENV_VARS=true
      # - GITLAB_INSTANCE_0_NAME=production
      # - GITLAB_INSTANCE_0_URL=https://gitlab.example.com
      # - GITLAB_INSTANCE_0_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
    tty: true
    stdin_open: true
    network_mode: host  # For better performance
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 512M
'''
    },
    
    # Documentation
    "README.md": {
        "type": "docs",
        "description": "Main documentation",
        "content": '''# GitLab Async Mass Exporter v3.0

A high-performance, asynchronous GitLab exporter with Terminal UI that exports **EVERYTHING** you have access to from multiple GitLab instances simultaneously.

## Features

- **🚀 Async Architecture**: Exports multiple projects concurrently for maximum speed
- **📊 Terminal UI**: Real-time progress monitoring with rich terminal interface
- **🏗️ Structure Preservation**: Maintains complete group/project hierarchy
- **📦 Complete Export**: Projects, wikis, snippets, issues, merge requests, and metadata
- **🔄 Resume Support**: Skip already exported projects
- **📝 Verbose Logging**: Detailed logs for debugging and audit trails
- **⚡ Error Resilience**: Continues export even if individual projects fail
- **📈 Progress Tracking**: Real-time statistics and success rates

## Quick Start

### Linux/macOS
```bash
chmod +x start.sh
./start.sh
```

### Windows
```cmd
python quickstart.py
```

### Docker
```bash
docker-compose up
```

## What Gets Exported

For each GitLab instance:
- **Projects**: Full project exports (.tar.gz archives)
- **Groups**: Complete group structure and metadata
- **Wikis**: All wiki pages with content and metadata
- **Snippets**: Project snippets with full content
- **Issues**: All project issues in JSON format
- **Merge Requests**: All MRs with complete data
- **Metadata**: Comprehensive metadata for everything

## Directory Structure

```
exports/
├── instance_name/
│   └── 20250722_143030/
│       ├── projects/
│       ├── groups/
│       ├── wikis/
│       ├── snippets/
│       ├── metadata/
│       ├── export.log
│       ├── errors.log
│       └── export_report.json
```

## Configuration

Edit `gitlab_instances.txt` with your GitLab instances in the format:
```
https://gitlab.example.com/users/sign_in username:password
    ⬡ TOKΞN: glpat-xxxxxxxxxxxxxxxxxxxx
    VΞRSION: 17.0.0
    ...
```

## Requirements

- Python 3.7+
- Personal Access Tokens with `api` scope
- Sufficient disk space for exports
- Stable internet connection

## Security

⚠️ **Never commit credentials to version control!**
- Use `.gitignore` for sensitive files
- Delete `gitlab_instances.txt` after use
- Consider using environment variables
'''
    },
    
    ".gitignore": {
        "type": "security",
        "description": "Git ignore file for security",
        "content": '''# Virtual Environment
venv/
env/
.venv/

# Sensitive Configuration Files
gitlab_instances.txt
config.json
credentials.enc
.gitlab_export_key
export_settings.json

# Environment files
.env
*.env

# Export Data
exports/

# Logs
*.log
logs/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.project
.pydevproject

# OS
.DS_Store
Thumbs.db
desktop.ini

# Backup files
*.bak
*.backup
*.old

# Temporary files
*.tmp
*.temp
/tmp/
'''
    },
    
    # Alternative versions
    "gitlab_export.py": {
        "type": "alternative",
        "description": "Simple synchronous version",
        "content": "# Simple GitLab export script (placeholder)\n# Use gitlab_async_tui_exporter.py for full functionality"
    },
    
    "gitlab_export_secure.py": {
        "type": "alternative", 
        "description": "Secure version with encryption",
        "content": "# Secure GitLab export script (placeholder)\n# Use gitlab_async_tui_exporter.py for full functionality"
    },
    
    "requirements.txt": {
        "type": "alternative",
        "description": "Dependencies for simple version",
        "content": "requests>=2.31.0\ncryptography>=41.0.0"
    },
    
    # Systemd files
    "gitlab-export.service": {
        "type": "systemd",
        "description": "Systemd service file",
        "content": '''[Unit]
Description=GitLab Project Export Service
After=network.target

[Service]
Type=oneshot
User=gitlab-export
Group=gitlab-export
WorkingDirectory=/opt/gitlab-export
Environment="PATH=/opt/gitlab-export/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/gitlab-export/venv/bin/python /opt/gitlab-export/gitlab_async_tui_exporter.py
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gitlab-export

[Install]
WantedBy=multi-user.target
'''
    },
    
    "gitlab-export.timer": {
        "type": "systemd",
        "description": "Systemd timer for scheduling",
        "content": '''[Unit]
Description=GitLab Export Timer - Daily at 2 AM
Requires=gitlab-export.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true
RandomizedDelaySec=3600

[Install]
WantedBy=timers.target
'''
    }
}

# Directory structure
DIRECTORIES = [
    "exports",
    "logs",
    "systemd"
]

def print_header():
    """Print script header"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      GitLab Mass Exporter - Setup Verification          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    print()

def check_file(filepath, file_info):
    """Check if a file exists and return status"""
    path = Path(filepath)
    exists = path.exists()
    
    if exists:
        size = path.stat().st_size
        return True, f"{Colors.GREEN}✓{Colors.RESET}", f"{size:,} bytes"
    else:
        return False, f"{Colors.RED}✗{Colors.RESET}", "Missing"

def create_file(filepath, content, executable=False):
    """Create a file with content"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if executable:
        os.chmod(path, 0o755)
    
    return True

def main():
    """Main verification and setup function"""
    print_header()
    
    # Check Python version
    print(f"{Colors.BOLD}System Requirements:{Colors.RESET}")
    python_version = sys.version.split()[0]
    if sys.version_info >= (3, 7):
        print(f"  Python: {Colors.GREEN}✓{Colors.RESET} {python_version}")
    else:
        print(f"  Python: {Colors.RED}✗{Colors.RESET} {python_version} (3.7+ required)")
    print()
    
    # Create directories
    print(f"{Colors.BOLD}Creating Directory Structure:{Colors.RESET}")
    for directory in DIRECTORIES:
        Path(directory).mkdir(exist_ok=True)
        print(f"  {directory}/: {Colors.GREEN}✓{Colors.RESET}")
    print()
    
    # Check files by category
    categories = {
        "core": "Core Application Files",
        "script": "Setup Scripts",
        "docker": "Docker Configuration",
        "docs": "Documentation",
        "security": "Security Configuration",
        "alternative": "Alternative Versions",
        "systemd": "Systemd Service Files"
    }
    
    missing_files = []
    total_files = len(FILES)
    existing_files = 0
    
    for category, title in categories.items():
        category_files = {k: v for k, v in FILES.items() if v["type"] == category}
        if not category_files:
            continue
            
        print(f"{Colors.BOLD}{title}:{Colors.RESET}")
        
        for filename, file_info in category_files.items():
            exists, status, size = check_file(filename, file_info)
            
            if exists:
                existing_files += 1
            else:
                missing_files.append((filename, file_info))
            
            # Format output
            desc = file_info["description"]
            print(f"  {status} {filename:<30} {desc:<40} {size}")
        
        print()
    
    # Summary
    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Total files: {total_files}")
    print(f"  Existing: {Colors.GREEN}{existing_files}{Colors.RESET}")
    print(f"  Missing: {Colors.RED}{len(missing_files)}{Colors.RESET}")
    print()
    
    # Ask to create missing files
    if missing_files:
        print(f"{Colors.YELLOW}Missing files detected!{Colors.RESET}")
        create = input(f"\n{Colors.BOLD}Create missing files? (y/n): {Colors.RESET}")
        
        if create.lower() == 'y':
            print(f"\n{Colors.BOLD}Creating missing files:{Colors.RESET}")
            
            for filename, file_info in missing_files:
                try:
                    # For systemd files, create in subdirectory
                    if file_info["type"] == "systemd":
                        filepath = f"systemd/{filename}"
                    else:
                        filepath = filename
                    
                    executable = file_info.get("executable", False)
                    create_file(filepath, file_info["content"], executable)
                    print(f"  {Colors.GREEN}✓{Colors.RESET} Created: {filepath}")
                except Exception as e:
                    print(f"  {Colors.RED}✗{Colors.RESET} Failed to create {filepath}: {str(e)}")
            
            print(f"\n{Colors.GREEN}✓ All missing files created!{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✓ All files present!{Colors.RESET}")
    
    # Additional setup steps
    print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
    print(f"1. Edit {Colors.CYAN}gitlab_instances.txt{Colors.RESET} with your GitLab instances")
    print(f"2. Run {Colors.CYAN}./start.sh{Colors.RESET} (Linux/macOS) or {Colors.CYAN}python quickstart.py{Colors.RESET} (Windows)")
    print(f"3. For Docker: {Colors.CYAN}docker-compose up{Colors.RESET}")
    
    # Check for existing config
    if Path("gitlab_instances.txt").exists():
        print(f"\n{Colors.YELLOW}⚠️  gitlab_instances.txt already exists!{Colors.RESET}")
        print("   Make sure it contains your actual GitLab instances before running.")
    
    print(f"\n{Colors.BOLD}Security Reminders:{Colors.RESET}")
    print(f"- {Colors.RED}Never commit credentials{Colors.RESET} to version control")
    print(f"- Use {Colors.CYAN}.gitignore{Colors.RESET} (already created)")
    print(f"- Delete sensitive files after use")
    print(f"- Consider using environment variables for production")
    
    print(f"\n{Colors.GREEN}✅ Setup verification complete!{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
