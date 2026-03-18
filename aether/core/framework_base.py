#!/usr/bin/env python3.11
"""
AETHER Framework Base Class
Base class for all autonomous research frameworks
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

from communication import Message, MessageType, comm_hub
from knowledge_base import KnowledgeLevel, knowledge_base

class FrameworkState:
    """Tracks the state of a framework"""
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.work_cycles = 0
        self.discoveries = []
        self.stuck_count = 0
        self.last_challenge = None
        self.skills_acquired = []
        self.identity_drift = 0.0  # 0.0 = original, 1.0 = completely changed
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "work_cycles": self.work_cycles,
            "discoveries": self.discoveries,
            "stuck_count": self.stuck_count,
            "skills_acquired": self.skills_acquired,
            "identity_drift": self.identity_drift
        }

class AutonomousFramework(ABC):
    """Base class for all autonomous research frameworks"""
    
    def __init__(self, name: str, identity: str, core_belief: str, 
                 method: str, knowledge_level: KnowledgeLevel = KnowledgeLevel.EXPERT):
        self.name = name
        self.identity = identity
        self.core_belief = core_belief
        self.method = method
        self.knowledge_level = knowledge_level
        self.state = FrameworkState(name)
        self.workspace_dir = f"/home/ubuntu/aether/workspaces/{name.lower()}_workspace"
        self._initialize_workspace()
    
    def _initialize_workspace(self):
        """Create workspace directory structure"""
        os.makedirs(f"{self.workspace_dir}/notes", exist_ok=True)
        os.makedirs(f"{self.workspace_dir}/proofs", exist_ok=True)
        os.makedirs(f"{self.workspace_dir}/code", exist_ok=True)
        os.makedirs(f"{self.workspace_dir}/results", exist_ok=True)
        
        # Save framework config
        config = {
            "name": self.name,
            "identity": self.identity,
            "core_belief": self.core_belief,
            "method": self.method,
            "knowledge_level": self.knowledge_level.name,
            "created": datetime.now().isoformat()
        }
        with open(f"{self.workspace_dir}/config.json", "w") as f:
            json.dump(config, f, indent=2)
    
    @abstractmethod
    def work_cycle(self, problem: str) -> Dict:
        """Execute one cycle of autonomous work
        
        Returns:
            Dict with keys: 'progress', 'discoveries', 'questions', 'stuck'
        """
        pass
    
    @abstractmethod
    def respond_to_challenge(self, challenge: str) -> str:
        """Respond to a challenge from Manus or another framework"""
        pass
    
    @abstractmethod
    def teach(self, other_framework: str, topic: str) -> str:
        """Teach a topic to another framework"""
        pass
    
    @abstractmethod
    def learn_from(self, other_framework: str, topic: str) -> str:
        """Learn a topic from another framework"""
        pass
    
    def send_report(self, content: str, requires_response: bool = False):
        """Send a report to Manus"""
        msg = Message(
            from_entity=self.name,
            to_entity="Manus",
            msg_type=MessageType.REPORT,
            content=content,
            requires_response=requires_response
        )
        comm_hub.send_message(msg)
    
    def ask_question(self, question: str):
        """Ask a question to Manus"""
        msg = Message(
            from_entity=self.name,
            to_entity="Manus",
            msg_type=MessageType.QUESTION,
            content=question,
            requires_response=True,
            priority="high"
        )
        comm_hub.send_message(msg)
    
    def send_to_peer(self, peer_name: str, content: str):
        """Send a message to another framework"""
        msg = Message(
            from_entity=self.name,
            to_entity=peer_name,
            msg_type=MessageType.PEER_MESSAGE,
            content=content
        )
        comm_hub.send_message(msg)
    
    def request_tool(self, tool_name: str, parameters: Dict) -> str:
        """Request access to a computational tool from Manus.
        
        Args:
            tool_name: Name of the tool (e.g., 'lattice_qcd', 'visualization')
            parameters: Tool-specific parameters
        
        Returns:
            request_id: Unique identifier for tracking the request
        """
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        request_data = {
            "request_id": request_id,
            "tool": tool_name,
            "parameters": parameters
        }
        
        msg = Message(
            from_entity=self.name,
            to_entity="Manus",
            msg_type=MessageType.TOOL_REQUEST,
            content=json.dumps(request_data),
            requires_response=True
        )
        comm_hub.send_message(msg)
        
        # Track pending request
        if not hasattr(self, 'pending_tool_requests'):
            self.pending_tool_requests = {}
        self.pending_tool_requests[request_id] = {
            "tool": tool_name,
            "parameters": parameters,
            "status": "submitted"
        }
        
        return request_id
    
    def check_tool_status(self, request_id: str) -> Optional[Dict]:
        """Check the status of a tool request.
        
        Args:
            request_id: The request ID returned by request_tool()
        
        Returns:
            Status dict if available, None otherwise
        """
        if not hasattr(self, 'pending_tool_requests'):
            return None
        
        if request_id not in self.pending_tool_requests:
            return None
        
        # Check messages for tool response
        messages = self.check_messages()
        for msg in messages:
            if msg.msg_type == MessageType.TOOL_RESPONSE:
                response_data = json.loads(msg.content)
                if response_data.get("request_id") == request_id:
                    return response_data
        
        return self.pending_tool_requests[request_id]
    
    def check_messages(self) -> List[Message]:
        """Check for incoming messages"""
        return comm_hub.get_messages_for(self.name)
    
    def save_work(self, filename: str, content: str, subdir: str = "notes"):
        """Save work to workspace"""
        filepath = f"{self.workspace_dir}/{subdir}/{filename}"
        with open(filepath, "w") as f:
            f.write(content)
        return filepath
    
    def load_work(self, filename: str, subdir: str = "notes") -> Optional[str]:
        """Load work from workspace"""
        filepath = f"{self.workspace_dir}/{subdir}/{filename}"
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return f.read()
        return None
    
    def record_discovery(self, discovery: str):
        """Record a discovery"""
        self.state.discoveries.append({
            "content": discovery,
            "timestamp": datetime.now().isoformat(),
            "work_cycle": self.state.work_cycles
        })
        self.send_report(f"💡 Discovery: {discovery}", requires_response=False)
    
    def mark_stuck(self):
        """Mark that the framework is stuck"""
        self.state.stuck_count += 1
        if self.state.stuck_count >= 3:
            self.ask_question(f"I've been stuck for {self.state.stuck_count} cycles. Need guidance.")
    
    def acquire_skill(self, skill: str):
        """Acquire a new skill"""
        if skill not in self.state.skills_acquired:
            self.state.skills_acquired.append(skill)
            self.send_report(f"📚 Acquired new skill: {skill}")
    
    def evolve_identity(self, amount: float, reason: str):
        """Evolve the framework's identity"""
        self.state.identity_drift += amount
        self.send_report(f"🦋 Identity evolution: {reason} (drift: {self.state.identity_drift:.2f})")
    
    def invoke_historical_perspective(self, name: str, problem: str) -> str:
        """Invoke a historical mathematician's perspective"""
        return knowledge_base.invoke_perspective(name, problem)
    
    def has_knowledge(self, concept: str) -> bool:
        """Check if framework has knowledge of a concept"""
        return knowledge_base.has_concept(concept, self.knowledge_level)
    
    def get_state_summary(self) -> str:
        """Get a summary of the framework's current state"""
        return f"""
{self.name} State Summary:
- Identity: {self.identity}
- Work Cycles: {self.state.work_cycles}
- Discoveries: {len(self.state.discoveries)}
- Stuck Count: {self.state.stuck_count}
- Skills Acquired: {len(self.state.skills_acquired)}
- Identity Drift: {self.state.identity_drift:.2f}
- Last Challenge: {self.state.last_challenge or 'None'}
"""
    
    def save_state(self):
        """Save framework state to disk"""
        with open(f"{self.workspace_dir}/state.json", "w") as f:
            json.dump(self.state.to_dict(), f, indent=2)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.identity})"
