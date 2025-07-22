# GitLab Mass Exporter - File List

## Core Files

### Main Application
- **`gitlab_async_tui_exporter.py`** - Main async TUI exporter with all features
- **`requirements-async.txt`** - Python dependencies for async version

### Setup & Configuration
- **`convert_config.py`** - Converts the provided format to config files
- **`gitlab_instances.txt`** - Your GitLab instances configuration (created on first run)
- **`config.json`** - Auto-generated standard config format

### Quick Start Scripts
- **`start.sh`** - Universal start script with menu (Linux/macOS)
- **`quickstart.py`** - Cross-platform quick start script
- **`setup_and_run.sh`** - Complete setup and run script (Linux/macOS)
- **`setup_and_run.bat`** - Complete setup and run script (Windows)

### Docker Support
- **`Dockerfile`** - Container image for the exporter
- **`docker-compose.yml`** - Docker Compose configuration

### Documentation
- **`README.md`** - Comprehensive documentation
- **`FILES.md`** - This file

## Alternative Versions (from earlier artifacts)

### Simple Version
- **`gitlab_export.py`** - Basic synchronous exporter
- **`requirements.txt`** - Dependencies for simple version

### Secure Version
- **`gitlab_export_secure.py`** - Version with encrypted credentials
- **`run_export.sh`** - Runner for secure version

### Systemd Service (for scheduled exports)
- **`gitlab-export.service`** - Systemd service file
- **`gitlab-export.timer`** - Systemd timer for scheduling

## Directory Structure After Running

```
project/
├── venv/                    # Python virtual environment
├── exports/                 # All exported data
│   └── instance_name/
│       └── timestamp/
│           ├── projects/    # Project exports with structure
│           ├── groups/      # Group metadata
│           ├── wikis/       # Wiki exports
│           ├── snippets/    # Code snippets
│           ├── metadata/    # Issues, MRs, etc.
│           ├── export.log   # Export log
│           ├── errors.log   # Error log
│           └── export_report.json
├── gitlab_instances.txt     # Your configuration
└── config.json             # Auto-generated config

```

## Usage Priority

1. **For most users**: Use `start.sh` or `quickstart.py`
2. **For Docker users**: Use `docker-compose up`
3. **For advanced users**: Use `gitlab_async_tui_exporter.py` directly
4. **For automation**: Use systemd service files

## Security Notes

⚠️ **Files containing sensitive data**:
- `gitlab_instances.txt` - Contains tokens (delete after use)
- `config.json` - Contains tokens (auto-generated)
- `credentials.enc` - Encrypted credentials (if using secure version)

Always add these to `.gitignore` and never commit to version control!
