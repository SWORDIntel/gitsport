#!/usr/bin/env python3
"""
Setup encrypted credentials for Docker deployment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gitlab_export_secure import SecureCredentialManager

def main():
    print("=== GitLab Docker Credentials Setup ===")
    print()
    print("This will create an encrypted credentials file for Docker deployment.")
    print("The file will be saved as 'credentials.enc' in the current directory.")
    print()
    
    cred_manager = SecureCredentialManager()
    config = cred_manager.setup_credentials()
    
    if config:
        print("\n✅ Credentials saved to 'credentials.enc'")
        print("\nTo use with Docker:")
        print("1. For batch mode with env vars:")
        print("   docker-compose -f docker-compose.secure.yml up gitlab-exporter-batch")
        print("\n2. For scheduled mode with encrypted file:")
        print("   docker-compose -f docker-compose.secure.yml up gitlab-exporter-scheduled")
        print("\n⚠️  Security reminder: Never commit credentials.enc to version control!")
    else:
        print("\n❌ Setup failed")

if __name__ == "__main__":
    main()