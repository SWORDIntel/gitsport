# GitLab Mass Exporter v3.0

A powerful, multi-version GitLab backup tool that exports all your accessible content from multiple GitLab instances. Choose from three implementations based on your needs: a beautiful async TUI, a secure encrypted version, or a simple straightforward exporter.

## 🚀 Features

- **🎨 Rich Terminal UI** - Beautiful async interface with real-time progress tracking
- **🔐 Encrypted Storage** - Secure credential management with password protection
- **📦 Complete Exports** - Projects, wikis, snippets, issues, and merge requests
- **⚡ Concurrent Downloads** - Export multiple projects simultaneously
- **🔄 Resume Support** - Skip already exported projects
- **🏢 Multi-Instance** - Export from multiple GitLab instances in one run
- **🐳 Docker Ready** - Run in containers with batch or scheduled modes
- **📊 Export Reports** - Detailed JSON reports of all operations

## 📥 Quick Start

### Option 1: Interactive Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/gitsport.git
cd gitsport

# Run the interactive setup
python3 quickstart.py
# OR
./start.sh
```

### Option 2: Direct Execution
```bash
# Install dependencies
pip install -r requirements-async.txt

# Run the async TUI version (recommended)
python3 gitlab_async_tui_exporter.py
```

### Option 3: Docker
```bash
# Run with Docker Compose
docker-compose up --build
```

## 🎯 Choose Your Version

### 1. **Async TUI Version** (Recommended for Interactive Use)
Beautiful terminal interface with real-time progress tracking.

```bash
python3 gitlab_async_tui_exporter.py
```

**Best for:**
- Interactive exports with visual feedback
- Selecting specific instances to export
- Monitoring progress in real-time

**Features:**
- Rich terminal UI with progress bars
- Concurrent async exports
- Interactive instance selection
- Exports projects, wikis, snippets, metadata

### 2. **Secure Version** (Recommended for Production)
Enterprise-grade with encrypted credential storage.

```bash
python3 gitlab_export_secure.py
```

**Best for:**
- Automated/scheduled exports
- CI/CD pipelines
- Production environments
- When security is paramount

**Features:**
- Encrypted credential storage
- Environment variable support
- Batch processing
- Comprehensive logging

### 3. **Simple Version** (Basic Export)
Straightforward synchronous exporter.

```bash
python3 gitlab_export.py
```

**Best for:**
- Quick one-off exports
- Single instance exports
- Minimal dependencies
- Simple use cases

## 📋 Configuration

### Method 1: config.json
Create a `config.json` file:
```json
{
  "instances": [
    {
      "name": "production",
      "url": "https://gitlab.example.com",
      "token": "glpat-xxxxxxxxxxxxxxxxxxxx"
    },
    {
      "name": "staging",
      "url": "https://gitlab-staging.example.com",
      "token": "glpat-yyyyyyyyyyyyyyyyyyyy"
    }
  ],
  "export_settings": {
    "max_concurrent_exports": 3,
    "timeout_minutes": 30
  }
}
```

### Method 2: Environment Variables (Secure Version)
```bash
export GITLAB_USE_ENV_VARS=true
export GITLAB_INSTANCE_0_NAME=production
export GITLAB_INSTANCE_0_URL=https://gitlab.example.com
export GITLAB_INSTANCE_0_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
```

### Method 3: Encrypted Credentials (Secure Version)
```bash
# Create encrypted credentials interactively
./setup-docker-credentials.py
```

## 📁 Export Structure

```
exports/
├── instance_name/
│   └── 20240722_143030/
│       ├── projects/          # Project tar.gz archives
│       ├── wikis/            # Wiki pages (async version)
│       ├── snippets/         # Code snippets (async version)
│       ├── metadata/         # Issues & MRs (async version)
│       ├── export.log        # Detailed export log
│       ├── errors.log        # Error log
│       ├── project_list.json # Project inventory
│       └── export_report.json # Summary report
```

## 🐳 Docker Usage

### Interactive Mode (Async TUI)
```bash
docker-compose up --build
```

### Batch Mode (One-time Export)
```bash
docker-compose -f docker-compose.secure.yml up gitlab-exporter-batch
```

### Scheduled Mode (Daily Exports)
```bash
docker-compose -f docker-compose.secure.yml up -d gitlab-exporter-scheduled
```

## 📊 Feature Comparison

| Feature | Async TUI | Secure | Simple |
|---------|-----------|---------|---------|
| Multiple Instances | ✅ | ✅ | ❌ |
| Visual Progress | ✅ Rich UI | ✅ Text | ✅ Basic |
| Concurrent Exports | ✅ | ✅ | ❌ |
| Encrypted Credentials | ❌ | ✅ | ❌ |
| Environment Variables | ❌ | ✅ | ❌ |
| Interactive Selection | ✅ | ❌ | ❌ |
| Wikis & Snippets | ✅ | ❌ | ❌ |
| Issues & MRs | ✅ | ❌ | ❌ |
| Docker Ready | ✅ | ✅ | ✅ |
| Resume Support | ✅ | ✅ | ✅ |

## 🔧 Requirements

- Python 3.7+
- GitLab Personal Access Token with `api` or `read_api` scope
- Dependencies:
  - Async TUI: `aiohttp`, `rich`
  - Secure: `requests`, `cryptography`
  - Simple: `requests`

## 📚 Documentation

- [Complete Usage Guide](USAGE_GUIDE.md) - Detailed usage instructions
- [Docker Usage](DOCKER_USAGE.md) - Docker-specific documentation
- [Project Status](PROJECT_STATUS.md) - Current implementation status

## 🔒 Security

- **Never commit credentials** - Use `.gitignore` for sensitive files
- **Use read-only tokens** - Only `read_api` scope needed
- **Encrypt credentials** - Use secure version for production
- **Rotate tokens regularly** - Update configurations as needed

## 🚦 Common Use Cases

### Daily Automated Backup
```bash
# Using systemd
sudo ./install-systemd.sh
sudo systemctl enable gitlab-export.timer

# Using Docker
docker-compose -f docker-compose.secure.yml up -d gitlab-exporter-scheduled
```

### CI/CD Pipeline Integration
```yaml
export-gitlab:
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python3 gitlab_export_secure.py
  artifacts:
    paths:
      - exports/
```

### Interactive Selection
```bash
# Use the async TUI for the best experience
python3 gitlab_async_tui_exporter.py
# Select which instances to export
# Watch real-time progress
```

## 🐛 Troubleshooting

### Connection Issues
- Verify GitLab URL includes `https://`
- Ensure token has `api` or `read_api` scope
- Test connection: `curl -H "PRIVATE-TOKEN: token" https://gitlab.example.com/api/v4/user`

### Export Failures
- Check available disk space
- Verify project export is enabled in GitLab settings
- Review `errors.log` in export directory
- Try reducing concurrent exports

### Performance
- Adjust `max_concurrent_exports` based on your system
- Large projects may timeout - increase `timeout_minutes`
- Run during off-peak hours for better performance

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions:
1. Check the [Usage Guide](USAGE_GUIDE.md)
2. Review logs in the export directory
3. Open an issue on GitHub

## 🔧 Enabling Project Export in GitLab

Project export must be enabled in your GitLab instance for this tool to work. Here's how to enable it:

### For GitLab Administrators

1. **Enable at Instance Level**:
   - Go to **Admin Area** → **Settings** → **General**
   - Expand **Visibility and access controls**
   - Check **Project export enabled**
   - Click **Save changes**

2. **Via GitLab Rails Console**:
   ```ruby
   # Enable project export
   ApplicationSetting.current.update!(project_export_enabled: true)
   
   # Verify it's enabled
   ApplicationSetting.current.project_export_enabled
   ```

3. **Via API** (requires admin token):
   ```bash
   curl --request PUT --header "PRIVATE-TOKEN: <admin-token>" \
     "https://gitlab.example.com/api/v4/application/settings?project_export_enabled=true"
   ```

### For Project Owners

If project export is enabled at the instance level, it's automatically available for all projects. You can verify by:

1. Going to **Project** → **Settings** → **General** → **Advanced**
2. Looking for the **Export project** button

### Troubleshooting Export Issues

If exports are failing:
- Check GitLab version (exports require GitLab 10.6+)
- Verify sufficient disk space on GitLab server
- Check Sidekiq is running (exports are processed asynchronously)
- Review GitLab logs: `/var/log/gitlab/gitlab-rails/production.log`

---

**Note**: This tool requires appropriate permissions on your GitLab instance. Ensure you have the necessary access rights and that project export is enabled as described above.
