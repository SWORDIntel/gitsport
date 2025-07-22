#!/usr/bin/env python3
"""
Secure GitLab Multi-Instance Export Script
Uses environment variables or encrypted credentials file
"""

import json
import os
import sys
import time
import requests
import getpass
from datetime import datetime
from pathlib import Path
import concurrent.futures
from urllib.parse import urlparse
from cryptography.fernet import Fernet
import base64
import hashlib

class SecureCredentialManager:
    def __init__(self, credentials_file="credentials.enc"):
        self.credentials_file = Path(credentials_file)
        self.key_file = Path(".gitlab_export_key")
        
    def generate_key_from_password(self, password):
        """Generate encryption key from password"""
        salt = b'gitlab_export_salt_v1'  # In production, use random salt
        kdf_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.urlsafe_b64encode(kdf_key)
    
    def encrypt_credentials(self, credentials, password):
        """Encrypt credentials with password"""
        key = self.generate_key_from_password(password)
        f = Fernet(key)
        encrypted = f.encrypt(json.dumps(credentials).encode())
        
        with open(self.credentials_file, 'wb') as file:
            file.write(encrypted)
        
        print(f"[INFO] Credentials encrypted and saved to {self.credentials_file}")
        
    def decrypt_credentials(self, password):
        """Decrypt credentials with password"""
        if not self.credentials_file.exists():
            return None
            
        key = self.generate_key_from_password(password)
        f = Fernet(key)
        
        with open(self.credentials_file, 'rb') as file:
            encrypted = file.read()
            
        try:
            decrypted = f.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception:
            print("[ERROR] Failed to decrypt credentials. Wrong password?")
            return None
    
    def setup_credentials(self):
        """Interactive setup for credentials"""
        print("\n[SETUP] GitLab Credentials Configuration")
        print("="*50)
        
        instances = []
        
        while True:
            print("\nAdd GitLab instance:")
            name = input("Instance name (e.g., production): ").strip()
            url = input("GitLab URL (e.g., https://gitlab.example.com): ").strip()
            
            # Check for token in environment variable first
            env_var_name = f"GITLAB_TOKEN_{name.upper()}"
            token = os.environ.get(env_var_name)
            
            if token:
                print(f"[INFO] Using token from environment variable: {env_var_name}")
            else:
                token = getpass.getpass("Personal Access Token (glpat-...): ").strip()
            
            instances.append({
                "name": name,
                "url": url,
                "token": token
            })
            
            another = input("\nAdd another instance? (y/n): ").lower()
            if another != 'y':
                break
        
        password = getpass.getpass("\nEnter password to encrypt credentials: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print("[ERROR] Passwords don't match!")
            return None
            
        credentials = {"instances": instances}
        self.encrypt_credentials(credentials, password)
        
        return credentials

class SecureGitLabExporter:
    def __init__(self, instance_config):
        self.base_url = instance_config['url'].rstrip('/')
        self.token = instance_config['token']
        self.instance_name = instance_config.get('name', urlparse(self.base_url).netloc)
        self.headers = {'PRIVATE-TOKEN': self.token}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Create export directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.export_dir = Path(f"exports/{self.instance_name}/{timestamp}")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file for this instance
        self.log_file = self.export_dir / "export.log"
        
    def log(self, message, level="INFO"):
        """Log to both console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def validate_connection(self):
        """Validate GitLab connection and token"""
        try:
            response = self.session.get(f"{self.base_url}/api/v4/user")
            if response.status_code == 200:
                user_info = response.json()
                self.log(f"Connected as: {user_info['username']} ({user_info['email']})")
                return True
            else:
                self.log(f"Authentication failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Connection failed: {str(e)}", "ERROR")
            return False
    
    def get_all_projects(self):
        """Fetch all projects with improved error handling"""
        if not self.validate_connection():
            return []
            
        projects = []
        page = 1
        
        while True:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/v4/projects",
                    params={
                        'membership': 'true',
                        'per_page': 100,
                        'page': page,
                        'order_by': 'id',
                        'sort': 'asc',
                        'archived': 'false'  # Skip archived projects by default
                    }
                )
                
                if response.status_code != 200:
                    self.log(f"Failed to fetch projects: {response.status_code}", "ERROR")
                    break
                    
                page_projects = response.json()
                if not page_projects:
                    break
                    
                projects.extend(page_projects)
                
                # Check if there are more pages
                if 'x-next-page' in response.headers and response.headers['x-next-page']:
                    page = int(response.headers['x-next-page'])
                else:
                    break
                    
            except Exception as e:
                self.log(f"Error fetching projects: {str(e)}", "ERROR")
                break
                
        return projects
    
    def export_project(self, project):
        """Export a single project with retry logic"""
        project_id = project['id']
        project_path = project['path_with_namespace']
        
        self.log(f"Starting export for: {project_path}")
        
        # Check if project was already exported
        filename = f"{project_path.replace('/', '_')}.tar.gz"
        filepath = self.export_dir / filename
        
        if filepath.exists():
            self.log(f"Already exported: {project_path}")
            return True
        
        # Trigger project export
        max_retries = 3
        for retry in range(max_retries):
            try:
                export_response = self.session.post(
                    f"{self.base_url}/api/v4/projects/{project_id}/export"
                )
                
                if export_response.status_code in [200, 202]:
                    break
                elif retry < max_retries - 1:
                    self.log(f"Export start failed for {project_path}, retrying...", "WARN")
                    time.sleep(5)
                else:
                    self.log(f"Failed to start export for {project_path}: {export_response.status_code}", "ERROR")
                    return False
                    
            except Exception as e:
                if retry < max_retries - 1:
                    self.log(f"Exception starting export for {project_path}, retrying: {str(e)}", "WARN")
                    time.sleep(5)
                else:
                    self.log(f"Exception starting export for {project_path}: {str(e)}", "ERROR")
                    return False
        
        # Poll export status
        max_attempts = 120  # 10 minutes timeout
        for attempt in range(max_attempts):
            try:
                status_response = self.session.get(
                    f"{self.base_url}/api/v4/projects/{project_id}/export"
                )
                
                if status_response.status_code != 200:
                    self.log(f"Failed to check export status for {project_path}", "ERROR")
                    return False
                    
                export_status = status_response.json()['export_status']
                
                if export_status == 'finished':
                    # Download the export
                    download_response = self.session.get(
                        f"{self.base_url}/api/v4/projects/{project_id}/export/download",
                        stream=True
                    )
                    
                    if download_response.status_code == 200:
                        # Save the export file with progress
                        total_size = int(download_response.headers.get('content-length', 0))
                        
                        with open(filepath, 'wb') as f:
                            downloaded = 0
                            for chunk in download_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    print(f"\r[PROGRESS] {project_path}: {progress:.1f}%", end='')
                        
                        print()  # New line after progress
                        self.log(f"Successfully exported: {project_path} ({total_size / 1024 / 1024:.1f} MB)")
                        return True
                    else:
                        self.log(f"Failed to download export for {project_path}", "ERROR")
                        return False
                        
                elif export_status == 'failed':
                    self.log(f"Export failed for {project_path}", "ERROR")
                    return False
                
                time.sleep(5)  # Wait 5 seconds before next check
                
            except Exception as e:
                self.log(f"Exception checking export status for {project_path}: {str(e)}", "ERROR")
                return False
                
        self.log(f"Export timed out for {project_path}", "ERROR")
        return False
    
    def export_all_projects(self, max_workers=3, include_archived=False):
        """Export all projects with improved concurrency"""
        projects = self.get_all_projects()
        
        if not projects:
            self.log(f"No projects found for {self.instance_name}")
            return
        
        self.log(f"Found {len(projects)} projects in {self.instance_name}")
        
        # Filter archived projects if needed
        if not include_archived:
            projects = [p for p in projects if not p.get('archived', False)]
            self.log(f"Exporting {len(projects)} active projects")
        
        # Write project list
        project_list_file = self.export_dir / "project_list.json"
        with open(project_list_file, 'w') as f:
            json.dump([{
                'id': p['id'],
                'name': p['name'],
                'path_with_namespace': p['path_with_namespace'],
                'web_url': p['web_url'],
                'archived': p.get('archived', False),
                'size': p.get('statistics', {}).get('repository_size', 0)
            } for p in projects], f, indent=2)
        
        # Sort projects by size (smaller first for better concurrency)
        projects.sort(key=lambda p: p.get('statistics', {}).get('repository_size', 0))
        
        # Export projects concurrently
        success_count = 0
        failed_projects = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_project = {
                executor.submit(self.export_project, project): project 
                for project in projects
            }
            
            for future in concurrent.futures.as_completed(future_to_project):
                project = future_to_project[future]
                try:
                    if future.result():
                        success_count += 1
                    else:
                        failed_projects.append(project['path_with_namespace'])
                except Exception as e:
                    self.log(f"Exception for {project['path_with_namespace']}: {str(e)}", "ERROR")
                    failed_projects.append(project['path_with_namespace'])
        
        # Summary
        self.log(f"\n{'='*60}")
        self.log(f"EXPORT SUMMARY for {self.instance_name}")
        self.log(f"  Total projects: {len(projects)}")
        self.log(f"  Successfully exported: {success_count}")
        self.log(f"  Failed: {len(failed_projects)}")
        self.log(f"  Export directory: {self.export_dir}")
        
        if failed_projects:
            failed_file = self.export_dir / "failed_exports.txt"
            with open(failed_file, 'w') as f:
                f.write('\n'.join(failed_projects))
            self.log(f"  Failed projects list: {failed_file}")

def main():
    print("[GITLAB EXPORT TOOL v2.0]")
    print("="*60)
    
    # Check for environment variable mode
    use_env_vars = os.environ.get('GITLAB_USE_ENV_VARS', '').lower() == 'true'
    
    if use_env_vars:
        # Load from environment variables
        instances = []
        i = 0
        while True:
            name = os.environ.get(f'GITLAB_INSTANCE_{i}_NAME')
            url = os.environ.get(f'GITLAB_INSTANCE_{i}_URL')
            token = os.environ.get(f'GITLAB_INSTANCE_{i}_TOKEN')
            
            if not all([name, url, token]):
                break
                
            instances.append({
                'name': name,
                'url': url,
                'token': token
            })
            i += 1
            
        if not instances:
            print("[ERROR] No GitLab instances found in environment variables!")
            print("\nSet environment variables like:")
            print("  GITLAB_USE_ENV_VARS=true")
            print("  GITLAB_INSTANCE_0_NAME=production")
            print("  GITLAB_INSTANCE_0_URL=https://gitlab.example.com")
            print("  GITLAB_INSTANCE_0_TOKEN=glpat-xxxxxxxxxxxx")
            sys.exit(1)
            
        config = {'instances': instances}
    else:
        # Use encrypted credentials
        cred_manager = SecureCredentialManager()
        
        if not cred_manager.credentials_file.exists():
            print("[INFO] No credentials file found. Starting setup...")
            config = cred_manager.setup_credentials()
            if not config:
                sys.exit(1)
        else:
            password = getpass.getpass("Enter password to decrypt credentials: ")
            config = cred_manager.decrypt_credentials(password)
            if not config:
                sys.exit(1)
    
    # Load export settings from config.json if exists
    config_file = Path("export_settings.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            settings = json.load(f)
            config['export_settings'] = settings.get('export_settings', {})
    
    # Export from each instance
    for instance_config in config.get('instances', []):
        print(f"\n{'='*60}")
        print(f"[START] Processing instance: {instance_config.get('name', instance_config['url'])}")
        print(f"{'='*60}")
        
        try:
            exporter = SecureGitLabExporter(instance_config)
            max_workers = config.get('export_settings', {}).get('max_concurrent_exports', 3)
            include_archived = config.get('export_settings', {}).get('include_archived', False)
            exporter.export_all_projects(max_workers=max_workers, include_archived=include_archived)
        except Exception as e:
            print(f"[ERROR] Failed to process instance: {str(e)}")
            continue
    
    print("\n[COMPLETE] All instances processed")

if __name__ == "__main__":
    main()