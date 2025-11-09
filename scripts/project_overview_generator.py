#!/usr/bin/env python3
"""Generate project overview from the enhanced CSV plan."""

import csv
import pathlib
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "project-plan.csv"
OUTPUT_PATH = ROOT / "docs" / "PROJECT_OVERVIEW.md"

def read_csv_plan() -> List[Dict[str, Any]]:
    """Read the enhanced CSV project plan."""
    rows = []
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        # Skip comments and metadata
        lines = [line for line in content.splitlines() 
                if line.strip() and not line.strip().startswith('#')]
        
        if not lines:
            return rows
            
        # Parse CSV
        reader = csv.DictReader(lines)
        for row in reader:
            if row.get('id') and not row['id'].startswith('#'):
                rows.append(row)
    
    return rows

def generate_phase_summary(tasks: List[Dict[str, Any]]) -> str:
    """Generate summary by phase."""
    phases = defaultdict(list)
    
    for task in tasks:
        phase = task.get('phase', 'unknown')
        phases[phase].append(task)
    
    lines = []
    lines.append("## Phase Summary\n")
    
    phase_order = ['foundation', 'agents', 'payments', 'optimization', 'business', 'maintenance']
    
    for phase in phase_order:
        if phase not in phases:
            continue
            
        phase_tasks = phases[phase]
        total = len(phase_tasks)
        completed = len([t for t in phase_tasks if t.get('status') == 'completed'])
        in_progress = len([t for t in phase_tasks if t.get('status') == 'in-progress'])
        
        # Calculate total estimated hours
        total_hours = sum(int(t.get('estimated_hours', 0)) for t in phase_tasks if t.get('estimated_hours'))
        
        progress_pct = int((completed / total) * 100) if total > 0 else 0
        status_emoji = "✅" if progress_pct == 100 else "🔄" if in_progress > 0 else "⏳"
        
        lines.append(f"### {status_emoji} {phase.title()} Phase")
        lines.append(f"- **Progress**: {completed}/{total} tasks ({progress_pct}%)")
        lines.append(f"- **Estimated Hours**: {total_hours}")
        lines.append(f"- **Status**: {in_progress} in progress, {total - completed - in_progress} remaining")
        lines.append("")
    
    return "\n".join(lines)

def generate_priority_breakdown(tasks: List[Dict[str, Any]]) -> str:
    """Generate breakdown by priority."""
    priorities = defaultdict(list)
    
    for task in tasks:
        priority = task.get('priority', 'P3')
        priorities[priority].append(task)
    
    lines = []
    lines.append("## Priority Breakdown\n")
    
    for priority in ['P0', 'P1', 'P2', 'P3']:
        if priority not in priorities:
            continue
            
        priority_tasks = priorities[priority]
        total = len(priority_tasks)
        completed = len([t for t in priority_tasks if t.get('status') == 'completed'])
        
        progress_pct = int((completed / total) * 100) if total > 0 else 0
        priority_name = {'P0': 'Critical', 'P1': 'High', 'P2': 'Medium', 'P3': 'Low'}[priority]
        
        lines.append(f"- **{priority} ({priority_name})**: {completed}/{total} ({progress_pct}%)")
    
    lines.append("")
    return "\n".join(lines)

def generate_upcoming_tasks(tasks: List[Dict[str, Any]]) -> str:
    """Generate list of upcoming high-priority tasks."""
    # Find tasks that are todo with high priority and no blocking dependencies
    completed_ids = {t['id'] for t in tasks if t.get('status') == 'completed'}
    
    upcoming = []
    for task in tasks:
        if task.get('status') != 'todo':
            continue
            
        # Check if dependencies are met
        deps = task.get('dependencies', '').strip()
        if deps:
            dep_ids = [dep.strip() for dep in deps.split(',') if dep.strip()]
            if not all(dep_id in completed_ids for dep_id in dep_ids):
                continue  # Dependencies not met
        
        # High priority tasks
        if task.get('priority') in ['P0', 'P1']:
            upcoming.append(task)
    
    # Sort by priority then estimated hours
    upcoming.sort(key=lambda t: (t.get('priority', 'P3'), int(t.get('estimated_hours', 0))))
    
    lines = []
    lines.append("## 🚀 Next Priorities (Unblocked)\n")
    
    for task in upcoming[:8]:  # Top 8 tasks
        hours = task.get('estimated_hours', 'TBD')
        deps = task.get('dependencies', '').strip()
        dep_note = f" (depends on {deps})" if deps else ""
        
        lines.append(f"- **{task['id']}**: {task.get('task', 'No description')} "
                    f"[{task.get('priority', 'P3')}, {hours}h, {task.get('owner', 'TBD')}]{dep_note}")
    
    lines.append("")
    return "\n".join(lines)

def main():
    """Generate the project overview."""
    tasks = read_csv_plan()
    
    if not tasks:
        print("No tasks found in CSV plan")
        return
    
    # Calculate overall statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
    in_progress_tasks = len([t for t in tasks if t.get('status') == 'in-progress'])
    total_hours = sum(int(t.get('estimated_hours', 0)) for t in tasks if t.get('estimated_hours'))
    completed_hours = sum(int(t.get('estimated_hours', 0)) for t in tasks 
                         if t.get('status') == 'completed' and t.get('estimated_hours'))
    
    overall_progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    # Generate the overview document
    content = f"""# CapeControl Project Overview

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Source: `docs/project-plan.csv` (Codex-Optimized Structure)*

## 📊 Project Status

- **Overall Progress**: {completed_tasks}/{total_tasks} tasks ({overall_progress}%)
- **Estimated Work**: {completed_hours}/{total_hours} hours completed
- **Active Tasks**: {in_progress_tasks} in progress
- **Project Version**: v0.3.0

{generate_phase_summary(tasks)}

{generate_priority_breakdown(tasks)}

{generate_upcoming_tasks(tasks)}

## 📋 Project Plan Structure

The enhanced project plan includes the following improvements for Codex integration:

- **Phase Organization**: Tasks grouped into logical development phases
- **Dependency Tracking**: Prerequisites clearly mapped for proper sequencing
- **Time Estimates**: Sprint planning and velocity tracking support
- **Codex Hints**: AI-specific development guidance for each task
- **Verification Commands**: Automated testing and validation steps
- **Artifact Paths**: Clear deliverable tracking with pipe-separated paths

## 🔗 Related Documentation

- **Project Plan**: `docs/project-plan.csv` (source data)
- **Implementation Guide**: `docs/PROJECT_PLAN_IMPROVEMENTS.md` 
- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE.md`
- **Development Context**: `docs/DEVELOPMENT_CONTEXT.md`

---
*This overview is automatically generated from the project plan CSV. Run `make project-overview` to regenerate.*
"""

    OUTPUT_PATH.write_text(content, encoding='utf-8')
    print(f"✅ Generated project overview at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
