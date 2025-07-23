#!/usr/bin/env python3
"""
GitLab Async TUI Mass Exporter
Exports all accessible content from multiple GitLab instances with structure preservation
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich.align import Align
from concurrent.futures import ThreadPoolExecutor
import tarfile
import base64
from typing import Dict, List, Any, Optional, Tuple, Callable
from functools import wraps
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
from urllib.parse import urlparse
import re
import random

console = Console()

def async_retry_with_backoff(retries=5, backoff_in_seconds=1):
    def r_decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            self = args[0]
            x = 0
            while True:
                try:
                    return await f(*args, **kwargs)
                except aiohttp.ClientResponseError as e:
                    if e.status == 429:
                        if x < retries:
                            sleep = (backoff_in_seconds * 2 ** x + random.random())
                            self.log(f"Rate limited. Retrying in {sleep:.2f} seconds.", "WARN")
                            self.stats.retries += 1
                            await asyncio.sleep(sleep)
                            x += 1
                        else:
                            self.log(f"Rate limited. Max retries exceeded.", "ERROR")
                            raise
                    else:
                        raise
        return wrapper
    return r_decorator

@dataclass
class GitLabInstance:
    name: str
    url: str
    token: str
    version: str = ""
    role: str = ""
    username: str = ""
    email: str = ""
    projects_count: int = 0
    groups_count: int = 0
    users_count: int = 0

@dataclass
class ExportStats:
    projects_exported: int = 0
    projects_failed: int = 0
    groups_exported: int = 0
    groups_failed: int = 0
    wikis_exported: int = 0
    snippets_exported: int = 0
    total_size: int = 0
    retries: int = 0
    start_time: float = field(default_factory=time.time)
    
    @property
    def elapsed_time(self):
        return time.time() - self.start_time
    
    @property
    def success_rate(self):
        total = self.projects_exported + self.projects_failed
        return (self.projects_exported / total * 100) if total > 0 else 0

class GitLabAsyncExporter:
    """Async GitLab exporter with progress tracking"""
    
    def __init__(self, instance: GitLabInstance, export_dir: Path, max_concurrent_downloads: int = 5, max_concurrent_api_calls: int = 10):
        self.instance = instance
        self.export_dir = export_dir / instance.name / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent_downloads = max_concurrent_downloads
        self.max_concurrent_api_calls = max_concurrent_api_calls
        self.stats = ExportStats()
        self.failed_projects = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.progress: Optional[Progress] = None
        self.log_file = self.export_dir / "export.log"
        self.error_file = self.export_dir / "errors.log"
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=300, connect=30, sock_connect=30, sock_read=300)
        self.session = aiohttp.ClientSession(
            headers={'PRIVATE-TOKEN': self.instance.token},
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def log(self, message: str, level: str = "INFO", to_file: bool = True):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        if level == "ERROR":
            console.print(f"[red]{log_entry}[/red]")
            if to_file:
                with open(self.error_file, 'a') as f:
                    f.write(log_entry + '\n')
        elif level == "SUCCESS":
            console.print(f"[green]{log_entry}[/green]")
        elif level == "WARN":
            console.print(f"[yellow]{log_entry}[/yellow]")
        else:
            console.print(log_entry)
            
        if to_file and level != "ERROR":
            with open(self.log_file, 'a') as f:
                f.write(log_entry + '\n')
                
    async def validate_connection(self) -> bool:
        """Validate GitLab connection and get user info"""
        try:
            async with self.session.get(f"{self.instance.url}/api/v4/user") as response:
                if response.status == 200:
                    user_data = await response.json()
                    self.instance.username = user_data.get('username', '')
                    self.instance.email = user_data.get('email', '')
                    
                    # Get version
                    async with self.session.get(f"{self.instance.url}/api/v4/version") as ver_response:
                        if ver_response.status == 200:
                            version_data = await ver_response.json()
                            self.instance.version = version_data.get('version', '')
                            
                    self.log(f"Connected to {self.instance.name} as {self.instance.username}", "SUCCESS")
                    return True
                else:
                    self.log(f"Authentication failed: {response.status}", "ERROR")
                    return False
        except Exception as e:
            self.log(f"Connection failed: {str(e)}", "ERROR")
            return False
            
    async def get_all_projects(self, semaphore: asyncio.Semaphore, task_id: Optional[int] = None) -> List[Dict]:
        """Fetch all accessible projects"""
        projects = []
        page = 1
        per_page = 100
        
        while True:
            try:
                params = {
                    'membership': 'true',
                    'per_page': per_page,
                    'page': page,
                    'order_by': 'id',
                    'sort': 'asc',
                    'statistics': 'true',
                    'with_issues_enabled': 'true',
                    'with_merge_requests_enabled': 'true'
                }
                
                async with semaphore:
                    async with self.session.get(
                        f"{self.instance.url}/api/v4/projects",
                        params=params
                    ) as response:
                        if response.status != 200:
                            self.log(f"Failed to fetch projects page {page}: {response.status}", "ERROR")
                            break

                        page_projects = await response.json()
                    if not page_projects:
                        break
                        
                    projects.extend(page_projects)
                    
                    if self.progress and task_id is not None:
                        self.progress.update(task_id, advance=len(page_projects))
                    
                    # Check for next page
                    if 'x-next-page' in response.headers and response.headers['x-next-page']:
                        page = int(response.headers['x-next-page'])
                    else:
                        break
                        
            except Exception as e:
                self.log(f"Error fetching projects page {page}: {str(e)}", "ERROR")
                break
                
        self.instance.projects_count = len(projects)
        return projects
        
    @async_retry_with_backoff()
    async def export_project(self, project: Dict, semaphore: asyncio.Semaphore, task_id: int) -> bool:
        """Export a single project"""
        async with semaphore:
            project_id = project['id']
            project_path = project['path_with_namespace']
            
            try:
                # Update progress
                if self.progress:
                    self.progress.update(task_id, description=f"[cyan]Exporting {project_path}...")
                
                # Check if already exported
                export_file = self.export_dir / "projects" / f"{project_path.replace('/', '_')}.tar.gz"
                if export_file.exists():
                    self.log(f"Already exported: {project_path}")
                    self.stats.projects_exported += 1
                    if self.progress:
                        self.progress.update(task_id, advance=1)
                    return True
                
                # Trigger export
                async with self.session.post(
                    f"{self.instance.url}/api/v4/projects/{project_id}/export"
                ) as response:
                    response.raise_for_status()

                    if response.status == 403:
                        self.log(f"Access forbidden to trigger export for {project_path}.", "ERROR")
                        self.stats.projects_failed += 1
                        self.failed_projects.append(project)
                        if self.progress:
                            self.progress.update(task_id, advance=1)
                        return False

                    if response.status not in [200, 202]:
                        self.log(f"Failed to start export for {project_path}: {response.status}", "ERROR")
                        self.stats.projects_failed += 1
                        self.failed_projects.append(project)
                        if self.progress:
                            self.progress.update(task_id, advance=1)
                        return False
                
                # Poll export status
                max_attempts = 120  # 10 minutes
                for attempt in range(max_attempts):
                    await asyncio.sleep(5)
                    
                    async with self.session.get(
                        f"{self.instance.url}/api/v4/projects/{project_id}/export"
                    ) as response:
                        if response.status != 200:
                            continue
                            
                        export_data = await response.json()
                        export_status = export_data.get('export_status', '')
                        
                        if export_status == 'finished':
                            # Download export
                            success = await self.download_export(project_id, project_path, export_file)
                            if success:
                                self.stats.projects_exported += 1
                            else:
                                self.stats.projects_failed += 1
                            if self.progress:
                                self.progress.update(task_id, advance=1)
                            return success
                            
                        elif export_status == 'failed':
                            self.log(f"Export failed for {project_path}", "ERROR")
                            self.stats.projects_failed += 1
                            self.failed_projects.append(project)
                            if self.progress:
                                self.progress.update(task_id, advance=1)
                            return False
                
                # Timeout
                self.log(f"Export timeout for {project_path}", "ERROR")
                self.stats.projects_failed += 1
                self.failed_projects.append(project)
                if self.progress:
                    self.progress.update(task_id, advance=1)
                return False
                
            except Exception as e:
                self.log(f"Exception exporting {project_path}: {str(e)}", "ERROR")
                self.stats.projects_failed += 1
                self.failed_projects.append(project)
                if self.progress:
                    self.progress.update(task_id, advance=1)
                return False
                
    @async_retry_with_backoff()
    async def download_export(self, project_id: int, project_path: str, export_file: Path) -> bool:
        """Download project export file with resume support"""
        try:
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            headers = {}
            file_mode = 'wb'
            downloaded_size = 0

            if export_file.exists():
                downloaded_size = export_file.stat().st_size
                headers['Range'] = f'bytes={downloaded_size}-'
                file_mode = 'ab'

            async with self.session.get(
                f"{self.instance.url}/api/v4/projects/{project_id}/export/download",
                headers=headers
            ) as response:
                response.raise_for_status()

                if response.status == 403:
                    self.log(f"Access forbidden to download {project_path}.", "ERROR")
                    return False

                if response.status not in [200, 206]:
                    self.log(f"Failed to download export for {project_path}: {response.status}", "ERROR")
                    return False

                total_size = int(response.headers.get('Content-Length', 0))
                
                with open(export_file, file_mode) as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)

                self.stats.total_size += total_size
                size_in_mb = (downloaded_size + total_size) / 1024 / 1024
                
                if file_mode == 'ab':
                    self.log(f"Resumed and completed download for {project_path} ({size_in_mb:.1f} MB)", "SUCCESS")
                else:
                    self.log(f"Downloaded {project_path} ({size_in_mb:.1f} MB)", "SUCCESS")
                return True

        except Exception as e:
            self.log(f"Exception downloading {project_path}: {str(e)}", "ERROR")
            return False
            
    async def export_wikis(self, projects: List[Dict], semaphore: asyncio.Semaphore) -> None:
        """Export wikis for all projects"""
        wiki_count = 0
        
        for project in projects:
            if not project.get('wiki_enabled', False):
                continue
                
            try:
                wiki_path = self.export_dir / "wikis" / f"{project['path_with_namespace'].replace('/', '_')}"
                wiki_path.mkdir(parents=True, exist_ok=True)
                
                # Get wiki pages
                async with semaphore:
                    async with self.session.get(
                        f"{self.instance.url}/api/v4/projects/{project['id']}/wikis"
                    ) as response:
                        if response.status != 200:
                            continue

                        wiki_pages = await response.json()
                    if not wiki_pages:
                        continue
                        
                    # Save wiki metadata
                    with open(wiki_path / "wiki_index.json", 'w') as f:
                        json.dump(wiki_pages, f, indent=2)
                    
                    # Download each wiki page content
                    for page in wiki_pages:
                        slug = page['slug']
                        async with self.session.get(
                            f"{self.instance.url}/api/v4/projects/{project['id']}/wikis/{slug}"
                        ) as page_response:
                            if page_response.status == 200:
                                page_data = await page_response.json()
                                with open(wiki_path / f"{slug}.md", 'w') as f:
                                    f.write(page_data.get('content', ''))
                    
                    wiki_count += 1
                    self.stats.wikis_exported += 1
                    
            except Exception as e:
                self.log(f"Error exporting wiki for {project['path_with_namespace']}: {str(e)}", "ERROR")
                
        self.log(f"Exported {wiki_count} wikis", "SUCCESS")
        
    async def export_snippets(self, projects: List[Dict], semaphore: asyncio.Semaphore) -> None:
        """Export snippets for all projects"""
        snippet_count = 0
        
        for project in projects:
            try:
                # Get project snippets
                async with semaphore:
                    async with self.session.get(
                        f"{self.instance.url}/api/v4/projects/{project['id']}/snippets"
                    ) as response:
                        if response.status != 200:
                            continue

                        snippets = await response.json()
                    if not snippets:
                        continue
                        
                    snippet_path = self.export_dir / "snippets" / f"{project['path_with_namespace'].replace('/', '_')}"
                    snippet_path.mkdir(parents=True, exist_ok=True)
                    
                    for snippet in snippets:
                        # Get snippet content
                        async with self.session.get(
                            f"{self.instance.url}/api/v4/projects/{project['id']}/snippets/{snippet['id']}/raw"
                        ) as content_response:
                            if content_response.status == 200:
                                content = await content_response.text()
                                filename = f"{snippet['id']}_{snippet['file_name']}"
                                with open(snippet_path / filename, 'w') as f:
                                    f.write(content)
                                    
                                # Save metadata
                                with open(snippet_path / f"{snippet['id']}_metadata.json", 'w') as f:
                                    json.dump(snippet, f, indent=2)
                                    
                                snippet_count += 1
                                self.stats.snippets_exported += 1
                                
            except Exception as e:
                self.log(f"Error exporting snippets for {project['path_with_namespace']}: {str(e)}", "ERROR")
                
        self.log(f"Exported {snippet_count} snippets", "SUCCESS")
        
    async def export_metadata(self, projects: List[Dict], semaphore: asyncio.Semaphore) -> None:
        """Export project metadata (issues, merge requests, etc.)"""
        metadata_dir = self.export_dir / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        for project in projects:
            try:
                project_meta_dir = metadata_dir / f"{project['path_with_namespace'].replace('/', '_')}"
                project_meta_dir.mkdir(parents=True, exist_ok=True)
                
                # Export issues
                if project.get('issues_enabled', False):
                    issues = []
                    page = 1
                    while True:
                        async with semaphore:
                            async with self.session.get(
                                f"{self.instance.url}/api/v4/projects/{project['id']}/issues",
                                params={'page': page, 'per_page': 100}
                            ) as response:
                                if response.status != 200:
                                    break
                                page_issues = await response.json()
                            if not page_issues:
                                break
                            issues.extend(page_issues)
                            page += 1
                            
                    if issues:
                        with open(project_meta_dir / "issues.json", 'w') as f:
                            json.dump(issues, f, indent=2)
                            
                # Export merge requests
                if project.get('merge_requests_enabled', False):
                    mrs = []
                    page = 1
                    while True:
                        async with self.session.get(
                            f"{self.instance.url}/api/v4/projects/{project['id']}/merge_requests",
                            params={'page': page, 'per_page': 100}
                        ) as response:
                            if response.status != 200:
                                break
                            page_mrs = await response.json()
                            if not page_mrs:
                                break
                            mrs.extend(page_mrs)
                            page += 1
                            
                    if mrs:
                        with open(project_meta_dir / "merge_requests.json", 'w') as f:
                            json.dump(mrs, f, indent=2)
                            
            except Exception as e:
                self.log(f"Error exporting metadata for {project['path_with_namespace']}: {str(e)}", "ERROR")

class TUIInterface:
    """Rich TUI interface for GitLab exporter"""
    
    def __init__(self):
        self.console = Console()
        self.instances: List[GitLabInstance] = []
        self.layout = self.create_layout()
        
    def create_layout(self) -> Layout:
        """Create the TUI layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )
        
        layout["body"].split_row(
            Layout(name="sidebar", ratio=1),
            Layout(name="main", ratio=3)
        )
        
        return layout
        
    def update_header(self, title: str = "GitLab Async Mass Exporter v3.0"):
        """Update header panel"""
        header_text = Text(title, justify="center", style="bold cyan")
        self.layout["header"].update(Panel(header_text))
        
    def update_footer(self, stats: Optional[ExportStats] = None):
        """Update footer with statistics"""
        if stats:
            elapsed = time.strftime('%H:%M:%S', time.gmtime(stats.elapsed_time))
            footer_text = (
                f"Projects: [green]{stats.projects_exported}[/green] exported, "
                f"[red]{stats.projects_failed}[/red] failed | "
                f"Success Rate: [cyan]{stats.success_rate:.1f}%[/cyan] | "
                f"Total Size: [yellow]{stats.total_size / 1024 / 1024 / 1024:.2f} GB[/yellow] | "
                f"Elapsed: [magenta]{elapsed}[/magenta]"
            )
        else:
            footer_text = "Ready to export..."
            
        self.layout["footer"].update(Panel(footer_text, title="Statistics"))
        
    def display_instances(self):
        """Display GitLab instances in sidebar"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Instance", style="cyan")
        table.add_column("Projects", justify="right")
        table.add_column("Status", justify="center")
        
        for instance in self.instances:
            status = "✓" if instance.username else "?"
            table.add_row(
                instance.name,
                str(instance.projects_count),
                f"[green]{status}[/green]" if status == "✓" else f"[yellow]{status}[/yellow]"
            )
            
        self.layout["sidebar"].update(Panel(table, title="GitLab Instances"))
        
    async def load_instances(self) -> bool:
        """Load GitLab instances from configuration"""
        # Check for config.json first
        config_file = Path("config.json")
        instances_file = Path("gitlab_instances.txt")
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                for inst in config.get('instances', []):
                    self.instances.append(GitLabInstance(
                        name=inst['name'],
                        url=inst['url'],
                        token=inst['token']
                    ))
                    
        elif instances_file.exists():
            # Parse the custom format
            content = instances_file.read_text()
            lines = content.strip().split('\n')
            
            current_instance = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for instance URL line
                if line.startswith('http'):
                    parts = line.split()
                    if len(parts) >= 2:
                        url = parts[0]
                        name = urlparse(url).netloc.split('.')[0]
                        current_instance = GitLabInstance(name=name, url=url, token="")
                        self.instances.append(current_instance)
                        
                # Check for token line
                elif current_instance and 'TOKΞN:' in line or 'TOKEN:' in line:
                    token_match = re.search(r'TOK[ΞE]N:\s*(\S+)', line)
                    if token_match:
                        current_instance.token = token_match.group(1)
                        
        else:
            self.console.print("[red]No configuration found![/red]")
            self.console.print("Please create config.json or gitlab_instances.txt")
            return False
            
        return len(self.instances) > 0
        
    async def select_instances(self) -> List[GitLabInstance]:
        """Interactive instance selection"""
        if not self.instances:
            return []
            
        self.console.print("\n[bold cyan]Select GitLab instances to export:[/bold cyan]")
        selected = []
        
        for i, instance in enumerate(self.instances, 1):
            if Confirm.ask(f"Export from {instance.name} ({instance.url})?", default=True):
                selected.append(instance)
                
        return selected
        
    async def run_export(self, selected_instances: List[GitLabInstance]):
        """Run the export process with progress tracking"""
        config_file = Path("config.json")
        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)

        max_concurrent_downloads = Prompt.ask(
            "[bold cyan]Enter max concurrent downloads[/bold cyan]",
            default=str(config.get("max_concurrent_downloads", 5))
        )
        config["max_concurrent_downloads"] = int(max_concurrent_downloads)

        max_concurrent_api_calls = Prompt.ask(
            "[bold cyan]Enter max concurrent API calls[/bold cyan]",
            default=str(config.get("max_concurrent_api_calls", 10))
        )
        config["max_concurrent_api_calls"] = int(max_concurrent_api_calls)

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            for instance in selected_instances:
                self.console.print(f"\n[bold cyan]Processing {instance.name}...[/bold cyan]")
                
                async with GitLabAsyncExporter(
                    instance,
                    Path("exports"),
                    max_concurrent_downloads=int(max_concurrent_downloads),
                    max_concurrent_api_calls=int(max_concurrent_api_calls)
                ) as exporter:
                    exporter.progress = progress
                    
                    # Validate connection
                    if not await exporter.validate_connection():
                        self.console.print(f"[red]Failed to connect to {instance.name}[/red]")
                        continue
                        
                    # Update instance info
                    instance.username = exporter.instance.username
                    instance.version = exporter.instance.version
                    
                    # Fetch projects
                    fetch_task = progress.add_task(
                        f"[cyan]Fetching projects from {instance.name}...",
                        total=None
                    )
                    
                    projects = await exporter.get_all_projects(api_semaphore, fetch_task)
                    progress.remove_task(fetch_task)
                    
                    if not projects:
                        self.console.print(f"[yellow]No projects found in {instance.name}[/yellow]")
                        continue
                        
                    self.console.print(f"[green]Found {len(projects)} projects[/green]")
                    
                    # Export projects
                    export_task = progress.add_task(
                        f"[cyan]Exporting projects from {instance.name}...",
                        total=len(projects)
                    )
                    
                    # Create semaphores for concurrency control
                    download_semaphore = asyncio.Semaphore(exporter.max_concurrent_downloads)
                    api_semaphore = asyncio.Semaphore(exporter.max_concurrent_api_calls)

                    # Export all projects concurrently
                    export_tasks = [
                        exporter.export_project(project, download_semaphore, export_task)
                        for project in projects
                    ]
                    
                    await asyncio.gather(*export_tasks)
                    
                    # Export additional data
                    self.console.print(f"[cyan]Exporting wikis and snippets...[/cyan]")
                    await exporter.export_wikis(projects, api_semaphore)
                    await exporter.export_snippets(projects, api_semaphore)
                    await exporter.export_metadata(projects, api_semaphore)
                    
                    # Save export report
                    report = {
                        'instance': instance.name,
                        'url': instance.url,
                        'export_date': datetime.now().isoformat(),
                        'statistics': {
                            'total_projects': len(projects),
                            'projects_exported': exporter.stats.projects_exported,
                            'projects_failed': exporter.stats.projects_failed,
                            'wikis_exported': exporter.stats.wikis_exported,
                            'snippets_exported': exporter.stats.snippets_exported,
                            'total_size_gb': exporter.stats.total_size / 1024 / 1024 / 1024,
                            'elapsed_seconds': exporter.stats.elapsed_time,
                            'success_rate': exporter.stats.success_rate,
                            'retries': exporter.stats.retries
                        },
                        'failed_projects': [p['path_with_namespace'] for p in exporter.failed_projects]
                    }
                    
                    with open(exporter.export_dir / "export_report.json", 'w') as f:
                        json.dump(report, f, indent=2)
                        
                    # Display summary
                    self.console.print(f"\n[bold green]Export Summary for {instance.name}:[/bold green]")
                    summary_table = Table(show_header=False)
                    summary_table.add_column("Metric", style="cyan")
                    summary_table.add_column("Value", justify="right")
                    
                    summary_table.add_row("Projects Exported", str(exporter.stats.projects_exported))
                    summary_table.add_row("Projects Failed", str(exporter.stats.projects_failed))
                    summary_table.add_row("Retries", str(exporter.stats.retries))
                    summary_table.add_row("Wikis Exported", str(exporter.stats.wikis_exported))
                    summary_table.add_row("Snippets Exported", str(exporter.stats.snippets_exported))
                    summary_table.add_row("Total Size", f"{exporter.stats.total_size / 1024 / 1024 / 1024:.2f} GB")
                    summary_table.add_row("Success Rate", f"{exporter.stats.success_rate:.1f}%")
                    summary_table.add_row("Export Location", str(exporter.export_dir))
                    
                    self.console.print(summary_table)

async def main():
    """Main entry point"""
    tui = TUIInterface()
    
    # Display header
    console.print("\n[bold cyan]GitLab Async Mass Exporter v3.0[/bold cyan]")
    console.print("=" * 60)
    
    # Load configuration
    if not await tui.load_instances():
        # Offer to create configuration
        if Confirm.ask("\nWould you like to create a configuration file?"):
            os.system("python convert_config.py")
            console.print("\n[yellow]Please edit gitlab_instances.txt and run again.[/yellow]")
        return
        
    # Display instances
    console.print(f"\n[green]Found {len(tui.instances)} GitLab instance(s)[/green]")
    
    # Select instances
    selected = await tui.select_instances()
    if not selected:
        console.print("\n[yellow]No instances selected. Exiting.[/yellow]")
        return
        
    # Confirm export
    console.print(f"\n[bold]Ready to export from {len(selected)} instance(s)[/bold]")
    if not Confirm.ask("Proceed with export?", default=True):
        console.print("\n[yellow]Export cancelled.[/yellow]")
        return
        
    # Run export
    try:
        await tui.run_export(selected)
        console.print("\n[bold green]✅ All exports completed![/bold green]")
    except KeyboardInterrupt:
        console.print("\n[red]Export interrupted by user[/red]")
    except Exception as e:
        console.print(f"\n[red]Export failed: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
