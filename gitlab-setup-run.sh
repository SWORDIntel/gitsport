#!/bin/bash
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
echo "   This will export:"
echo "   • All projects (with full export archives)"
echo "   • All groups (preserving structure)"
echo "   • All wikis"
echo "   • All snippets"
echo "   • All issues and merge requests"
echo "   • Complete metadata"
echo
echo "⚠️  WARNING: This may take a long time for large instances!"
echo

# Run the exporter
python3 gitlab_async_tui_exporter.py

# Deactivate virtual environment
deactivate

echo
echo "✅ Export process completed!"
echo "📁 Check the 'exports' directory for your data"
