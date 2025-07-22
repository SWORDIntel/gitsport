#!/usr/bin/env python3
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
    print("\nThis file will be automatically converted to config.json when you run the exporter.")
    print("\n⚠️  SECURITY WARNING: Replace with your actual credentials!")
    print("\nThe async TUI exporter will:")
    print("  1. Read gitlab_instances.txt")
    print("  2. Parse all GitLab instances")
    print("  3. Create config.json automatically")
    print("  4. Export ALL accessible content from each instance")
    print("\nRun: python gitlab_async_tui_exporter.py")

if __name__ == "__main__":
    convert_config()