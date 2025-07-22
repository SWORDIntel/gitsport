#!/usr/bin/env python3
"""
Simple GitLab Export Script
Basic synchronous version for single instance exports
"""

import json
import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SimpleGitLabExporter:
    """Simple synchronous GitLab exporter"""
    
    def __init__(self, url: str, token: str, export_dir: str = "exports"):
        self.base_url = url.rstrip('/')
        self.token = token
        self.headers = {'PRIVATE-TOKEN': token}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Create export directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        instance_name = url.split('//')[1].split('/')[0].replace('.', '_')
        self.export_dir = Path(export_dir) / instance_name / timestamp
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'projects_exported': 0,
            'projects_failed': 0,
            'total_size': 0,
            'start_time': time.time()
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Simple logging to console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
        
    def validate_connection(self) -> bool:
        """Test GitLab connection"""
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
            
    def get_all_projects(self) -> List[Dict]:
        """Fetch all accessible projects"""
        projects = []
        page = 1
        
        self.log("Fetching projects...")
        
        while True:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/v4/projects",
                    params={
                        'membership': 'true',
                        'per_page': 100,
                        'page': page,
                        'order_by': 'id',
                        'sort': 'asc'
                    }
                )
                
                if response.status_code != 200:
                    self.log(f"Failed to fetch projects: {response.status_code}", "ERROR")
                    break
                    
                page_projects = response.json()
                if not page_projects:
                    break
                    
                projects.extend(page_projects)
                self.log(f"Fetched page {page} ({len(page_projects)} projects)")
                
                # Check for next page
                if 'x-next-page' in response.headers and response.headers['x-next-page']:
                    page = int(response.headers['x-next-page'])
                else:
                    break
                    
            except Exception as e:
                self.log(f"Error fetching projects: {str(e)}", "ERROR")
                break
                
        self.log(f"Found {len(projects)} total projects")
        return projects
        
    def export_project(self, project: Dict) -> bool:
        """Export a single project"""
        project_id = project['id']
        project_path = project['path_with_namespace']
        
        self.log(f"Exporting: {project_path}")
        
        # Check if already exported
        filename = f"{project_path.replace('/', '_')}.tar.gz"
        filepath = self.export_dir / "projects" / filename
        
        if filepath.exists():
            self.log(f"Already exported: {project_path}")
            self.stats['projects_exported'] += 1
            return True
            
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Trigger export
        try:
            export_response = self.session.post(
                f"{self.base_url}/api/v4/projects/{project_id}/export"
            )
            
            if export_response.status_code not in [200, 202]:
                self.log(f"Failed to start export for {project_path}: {export_response.status_code}", "ERROR")
                self.stats['projects_failed'] += 1
                return False
                
        except Exception as e:
            self.log(f"Exception starting export for {project_path}: {str(e)}", "ERROR")
            self.stats['projects_failed'] += 1
            return False
            
        # Poll export status
        max_attempts = 120  # 10 minutes
        for attempt in range(max_attempts):
            time.sleep(5)
            
            try:
                status_response = self.session.get(
                    f"{self.base_url}/api/v4/projects/{project_id}/export"
                )
                
                if status_response.status_code != 200:
                    continue
                    
                export_status = status_response.json()['export_status']
                
                if export_status == 'finished':
                    # Download export
                    download_response = self.session.get(
                        f"{self.base_url}/api/v4/projects/{project_id}/export/download",
                        stream=True
                    )
                    
                    if download_response.status_code == 200:
                        total_size = int(download_response.headers.get('content-length', 0))
                        
                        with open(filepath, 'wb') as f:
                            downloaded = 0
                            for chunk in download_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    print(f"\r  Progress: {progress:.1f}%", end='')
                                    
                        print()  # New line after progress
                        
                        self.stats['total_size'] += total_size
                        self.stats['projects_exported'] += 1
                        self.log(f"Successfully exported: {project_path} ({total_size / 1024 / 1024:.1f} MB)")
                        return True
                    else:
                        self.log(f"Failed to download export for {project_path}", "ERROR")
                        self.stats['projects_failed'] += 1
                        return False
                        
                elif export_status == 'failed':
                    self.log(f"Export failed for {project_path}", "ERROR")
                    self.stats['projects_failed'] += 1
                    return False
                    
            except Exception as e:
                self.log(f"Exception checking export status for {project_path}: {str(e)}", "ERROR")
                continue
                
        self.log(f"Export timeout for {project_path}", "ERROR")
        self.stats['projects_failed'] += 1
        return False
        
    def export_all_projects(self, include_archived: bool = False):
        """Export all projects"""
        projects = self.get_all_projects()
        
        if not projects:
            self.log("No projects found")
            return
            
        # Filter archived if needed
        if not include_archived:
            projects = [p for p in projects if not p.get('archived', False)]
            self.log(f"Exporting {len(projects)} active projects")
            
        # Save project list
        project_list_file = self.export_dir / "project_list.json"
        with open(project_list_file, 'w') as f:
            json.dump([{
                'id': p['id'],
                'name': p['name'],
                'path_with_namespace': p['path_with_namespace'],
                'web_url': p['web_url']
            } for p in projects], f, indent=2)
            
        # Export each project
        for i, project in enumerate(projects, 1):
            self.log(f"\n[{i}/{len(projects)}] Processing {project['path_with_namespace']}")
            self.export_project(project)
            
        # Display summary
        elapsed_time = time.time() - self.stats['start_time']
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        
        self.log("\n" + "="*60)
        self.log("EXPORT SUMMARY")
        self.log(f"  Total projects: {len(projects)}")
        self.log(f"  Successfully exported: {self.stats['projects_exported']}")
        self.log(f"  Failed: {self.stats['projects_failed']}")
        self.log(f"  Total size: {self.stats['total_size'] / 1024 / 1024 / 1024:.2f} GB")
        self.log(f"  Time elapsed: {elapsed_str}")
        self.log(f"  Export directory: {self.export_dir}")
        self.log("="*60)

def main():
    """Main entry point"""
    print("GitLab Simple Export Tool v1.0")
    print("="*40)
    
    # Check for config file
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        instances = config.get('instances', [])
        if not instances:
            print("No instances found in config.json")
            sys.exit(1)
            
        # Use first instance for simple version
        instance = instances[0]
        url = instance['url']
        token = instance['token']
        
        print(f"Using instance: {instance['name']} ({url})")
        
    else:
        # Prompt for credentials
        print("\nNo config.json found. Please enter GitLab details:")
        url = input("GitLab URL (e.g., https://gitlab.example.com): ").strip()
        token = input("Personal Access Token: ").strip()
        
    # Create exporter and run
    exporter = SimpleGitLabExporter(url, token)
    
    # Validate connection
    if not exporter.validate_connection():
        print("\nFailed to connect to GitLab. Please check your URL and token.")
        sys.exit(1)
        
    # Export all projects
    try:
        exporter.export_all_projects()
    except KeyboardInterrupt:
        print("\n\nExport interrupted by user")
    except Exception as e:
        print(f"\n\nExport failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()