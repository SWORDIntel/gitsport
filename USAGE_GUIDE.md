# GitLab Mass Exporter - Complete Usage Guide

## Quick Start

### 1. First Time Setup
```bash
# Clone or download the project
cd gitsport

# Run the quickstart script
python3 quickstart.py
# OR
./start.sh
```

### 2. Choose Your Version

#### 🎨 Async TUI Version (Recommended for Interactive Use)
- **Best for**: Interactive exports with visual progress
- **Features**: Beautiful UI, concurrent exports, real-time stats
```bash
python3 gitlab_async_tui_exporter.py
```

#### 🔐 Secure Version (Recommended for Production)
- **Best for**: Automated/scheduled exports, CI/CD
- **Features**: Encrypted credentials, environment variables
```bash
python3 gitlab_export_secure.py
```

#### 📦 Simple Version (Basic Export)
- **Best for**: Quick single-instance exports
- **Features**: Minimal dependencies, straightforward
```bash
python3 gitlab_export.py
```

## Configuration Options

### Option 1: config.json (All Versions)
```json
{
  "instances": [
    {
      "name": "production",
      "url": "https://gitlab.example.com",
      "token": "glpat-xxxxxxxxxxxxxxxxxxxx"
    }
  ],
  "export_settings": {
    "max_concurrent_exports": 3,
    "timeout_minutes": 30
  }
}
```

### Option 2: gitlab_instances.txt (Async TUI)
```
https://gitlab.example.com/users/sign_in user:password
    ⬡ TOKΞN: glpat-xxxxxxxxxxxxxxxxxxxx
    VΞRSION: 17.0.0
    ROLΞ: Administrator
```

### Option 3: Environment Variables (Secure Version)
```bash
export GITLAB_USE_ENV_VARS=true
export GITLAB_INSTANCE_0_NAME=production
export GITLAB_INSTANCE_0_URL=https://gitlab.example.com
export GITLAB_INSTANCE_0_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
```

### Option 4: Encrypted Credentials (Secure Version)
```bash
# Create encrypted credentials
./setup-docker-credentials.py

# Use with secure version
python3 gitlab_export_secure.py
```

## Docker Usage

### Interactive Mode (Async TUI)
```bash
# Build and run interactively
docker-compose up --build

# Or use pre-built image
docker run -it \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $(pwd)/exports:/app/exports \
  gitlab-exporter
```

### Batch Mode (Secure Version)
```bash
# One-time export
docker-compose -f docker-compose.secure.yml up gitlab-exporter-batch

# Scheduled exports (runs every 24h)
docker-compose -f docker-compose.secure.yml up -d gitlab-exporter-scheduled
```

## Feature Comparison

| Feature | Async TUI | Secure | Simple |
|---------|-----------|---------|---------|
| Multiple Instances | ✅ | ✅ | ❌ (first only) |
| Visual Progress | ✅ Rich UI | ✅ Text | ✅ Basic |
| Concurrent Exports | ✅ | ✅ | ❌ |
| Encrypted Credentials | ❌ | ✅ | ❌ |
| Environment Variables | ❌ | ✅ | ❌ |
| Interactive Selection | ✅ | ❌ | ❌ |
| Wikis & Snippets | ✅ | ❌ | ❌ |
| Issues & MRs | ✅ | ❌ | ❌ |
| Resume Support | ✅ | ✅ | ✅ |
| Docker Ready | ✅* | ✅ | ✅ |

*Requires interactive mode

## Export Structure

All versions create a similar directory structure:
```
exports/
├── instance_name/
│   └── 20240722_143030/
│       ├── projects/          # Project tar.gz files
│       ├── wikis/            # Wiki content (async only)
│       ├── snippets/         # Code snippets (async only)
│       ├── metadata/         # Issues, MRs (async only)
│       ├── export.log        # Export log
│       ├── errors.log        # Error log
│       ├── project_list.json # Project inventory
│       └── export_report.json # Summary report
```

## Common Use Cases

### 1. Daily Backup of Production
```bash
# Using systemd timer
sudo ./install-systemd.sh
sudo systemctl enable gitlab-export.timer

# Or Docker scheduled mode
docker-compose -f docker-compose.secure.yml up -d gitlab-exporter-scheduled
```

### 2. Interactive Export with Selection
```bash
# Use async TUI for best experience
python3 gitlab_async_tui_exporter.py
# Select which instances to export
# Watch real-time progress
```

### 3. CI/CD Pipeline Export
```yaml
# .gitlab-ci.yml example
export:
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - export GITLAB_USE_ENV_VARS=true
    - python3 gitlab_export_secure.py
  artifacts:
    paths:
      - exports/
```

### 4. Quick Single Instance Export
```bash
# Simple version prompts for credentials
python3 gitlab_export.py
# Enter URL and token when prompted
```

## Troubleshooting

### Connection Issues
- Verify GitLab URL (include https://)
- Check token has `api` or `read_api` scope
- Test with: `curl -H "PRIVATE-TOKEN: your-token" https://gitlab.example.com/api/v4/user`

### Export Failures
- Check available disk space
- Verify project export is enabled on GitLab
- Look in `errors.log` for specific issues
- Try reducing concurrent exports

### Docker Issues
- Async TUI requires TTY: use `-it` flag
- Ensure volumes are mounted correctly
- Check file permissions on mounted configs

### Performance
- Reduce concurrent exports for large projects
- Use secure version for better performance
- Consider running during off-peak hours

## Security Best Practices

1. **Never commit tokens** - Use .gitignore
2. **Use read-only tokens** - Minimum required scope
3. **Encrypt credentials** - Use secure version for production
4. **Rotate tokens regularly** - Update configs as needed
5. **Secure export directory** - Limit access to exports

## Advanced Configuration

### Custom Export Settings
Create `export_settings.json`:
```json
{
  "export_settings": {
    "max_concurrent_exports": 5,
    "include_archived": false,
    "timeout_minutes": 60,
    "retry_failed": true,
    "verify_ssl": true
  }
}
```

### Multi-Region Setup
```bash
# Region 1
GITLAB_INSTANCE_0_NAME=us-prod
GITLAB_INSTANCE_0_URL=https://gitlab-us.company.com
GITLAB_INSTANCE_0_TOKEN=glpat-us-xxxxx

# Region 2  
GITLAB_INSTANCE_1_NAME=eu-prod
GITLAB_INSTANCE_1_URL=https://gitlab-eu.company.com
GITLAB_INSTANCE_1_TOKEN=glpat-eu-xxxxx
```

## Support

For issues or questions:
1. Check the logs in export directory
2. Review this guide and PROJECT_STATUS.md
3. Try with simple version first to isolate issues
4. Enable debug logging if available