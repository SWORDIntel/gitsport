#!/bin/bash
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
