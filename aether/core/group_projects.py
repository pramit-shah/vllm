#!/usr/bin/env python3.11
"""
AETHER Group Projects System

4 group projects across the entire learning journey:
- Triggered randomly, not per session
- Helps frameworks discover complementary skills
- Prepares them for collaboration (without telling them)
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional


# 4 Group Projects across the journey
GROUP_PROJECTS = [
    {
        "id": "GP1",
        "name": "Number Patterns Discovery",
        "theme": "exploration",
        "description": "Work together to find and explain interesting number patterns",
        "trigger_range": (10, 50),  # Sessions 10-50
        "skills_revealed": ["pattern_recognition", "communication"],
        "tasks": [
            "Find 3 interesting number sequences",
            "Explain why each pattern works",
            "Create your own original pattern"
        ]
    },
    {
        "id": "GP2", 
        "name": "Geometry Construction Challenge",
        "theme": "problem_solving",
        "description": "Collaborate to solve geometric construction problems",
        "trigger_range": (60, 120),  # Sessions 60-120
        "skills_revealed": ["spatial_reasoning", "logical_thinking"],
        "tasks": [
            "Construct a regular hexagon using only compass and straightedge",
            "Prove why your construction works",
            "Extend to a more complex shape"
        ]
    },
    {
        "id": "GP3",
        "name": "Mathematical Proof Workshop",
        "theme": "research",
        "description": "Work together to understand and create mathematical proofs",
        "trigger_range": (150, 250),  # Sessions 150-250
        "skills_revealed": ["rigorous_thinking", "proof_construction"],
        "tasks": [
            "Study a classic proof together",
            "Identify the key logical steps",
            "Attempt to prove a related theorem"
        ]
    },
    {
        "id": "GP4",
        "name": "Open Problem Investigation",
        "theme": "advanced_research",
        "description": "Investigate an open mathematical problem together",
        "trigger_range": (300, 500),  # Sessions 300-500
        "skills_revealed": ["research_skills", "collaboration", "creativity"],
        "tasks": [
            "Research the background of the problem",
            "Identify what's known and unknown",
            "Propose potential approaches",
            "Document your findings"
        ]
    }
]


class GroupProjectManager:
    """Manages group projects across the learning journey."""
    
    def __init__(self, storage_dir: str = "/home/ubuntu/aether/memory"):
        self.storage_dir = storage_dir
        self.storage_path = os.path.join(storage_dir, "group_projects.json")
        
        # Track completed projects
        self.completed_projects: List[Dict] = []
        self.next_project_index = 0
        self.last_project_session = 0
        
        # Random trigger points for each project
        self.trigger_sessions: List[int] = []
        
        os.makedirs(storage_dir, exist_ok=True)
        self._load()
        self._initialize_triggers()
    
    def _load(self):
        """Load project history."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.completed_projects = data.get("completed_projects", [])
                    self.next_project_index = data.get("next_project_index", 0)
                    self.last_project_session = data.get("last_project_session", 0)
                    self.trigger_sessions = data.get("trigger_sessions", [])
            except:
                pass
    
    def save(self):
        """Save project history."""
        data = {
            "completed_projects": self.completed_projects,
            "next_project_index": self.next_project_index,
            "last_project_session": self.last_project_session,
            "trigger_sessions": self.trigger_sessions,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_triggers(self):
        """Initialize random trigger sessions for projects."""
        if not self.trigger_sessions:
            for project in GROUP_PROJECTS:
                min_session, max_session = project["trigger_range"]
                trigger = random.randint(min_session, max_session)
                self.trigger_sessions.append(trigger)
            self.save()
    
    def should_trigger_project(self, current_session: int) -> bool:
        """Check if a project should be triggered."""
        if self.next_project_index >= len(GROUP_PROJECTS):
            return False  # All projects completed
        
        # Minimum gap between projects
        if current_session - self.last_project_session < 20:
            return False
        
        # Check if we've reached the trigger session
        trigger = self.trigger_sessions[self.next_project_index]
        
        # Allow some randomness around the trigger point
        if current_session >= trigger:
            # 30% chance each session after trigger
            return random.random() < 0.3
        
        return False
    
    def assign_project(self, participants: List[str], session: int) -> Optional[Dict]:
        """Assign the next project to participants."""
        if self.next_project_index >= len(GROUP_PROJECTS):
            return None
        
        project = GROUP_PROJECTS[self.next_project_index].copy()
        project["participants"] = participants
        project["assigned_session"] = session
        project["assigned_date"] = datetime.now().isoformat()
        project["status"] = "assigned"
        
        self.completed_projects.append(project)
        self.next_project_index += 1
        self.last_project_session = session
        self.save()
        
        return project
    
    def get_project_summary(self) -> Dict:
        """Get summary of project progress."""
        return {
            "total_projects": len(GROUP_PROJECTS),
            "completed": len(self.completed_projects),
            "remaining": len(GROUP_PROJECTS) - self.next_project_index,
            "projects": self.completed_projects,
            "next_trigger": self.trigger_sessions[self.next_project_index] if self.next_project_index < len(GROUP_PROJECTS) else None
        }


# For simpler testing - trigger projects more frequently
class TestGroupProjectManager(GroupProjectManager):
    """Group project manager with more frequent triggers for testing."""
    
    def _initialize_triggers(self):
        """Initialize triggers at shorter intervals for testing."""
        if not self.trigger_sessions:
            # Trigger every ~15 sessions for testing
            self.trigger_sessions = [15, 35, 55, 80]
            self.save()
    
    def should_trigger_project(self, current_session: int) -> bool:
        """More frequent triggers for testing."""
        if self.next_project_index >= len(GROUP_PROJECTS):
            return False
        
        if current_session - self.last_project_session < 10:
            return False
        
        trigger = self.trigger_sessions[self.next_project_index]
        if current_session >= trigger:
            return random.random() < 0.5  # 50% chance
        
        return False
