#!/usr/bin/env python3
"""
Restart the GitLab export for projects that were skipped due to rate limiting.
"""

import json
import os
from pathlib import Path

def restart_export():
    """
    Restart the export for projects in the retry queue.
    """
    retry_queue_file = Path("retry_queue.json")
    if not retry_queue_file.exists():
        print("No projects in the retry queue.")
        return

    with open(retry_queue_file, 'r') as f:
        projects_to_retry = [json.loads(line) for line in f]

    if not projects_to_retry:
        print("No projects in the retry queue.")
        return

    project_ids = [str(p['id']) for p in projects_to_retry]

    # Clear the retry queue
    with open(retry_queue_file, 'w') as f:
        f.write("")

    print(f"Restarting export for {len(project_ids)} projects...")
    os.system(f"python gitlab_async_tui_exporter.py --projects {','.join(project_ids)}")

if __name__ == "__main__":
    restart_export()
