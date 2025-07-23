#!/usr/bin/env python3
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
        print("\n\n❌ Interrupted by user")
    except subprocess.CalledProcessError as e:
        print(f"\n\n❌ Error: Command failed with exit code {e.returncode}")
