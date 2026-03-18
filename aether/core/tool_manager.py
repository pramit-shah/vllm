"""
Tool Manager for AETHER System

Manus owns and manages all computational tools, multimodal capabilities,
and external access. Frameworks submit requests and receive results.

Architecture:
- Frameworks are lightweight (text-only, pure reasoning)
- Manus has full capabilities (compute, vision, research, generation)
- Request queue processes one at a time
- Results transferred back to requesters
"""

import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ToolRequest:
    """A request for tool access."""
    request_id: str
    requester: str  # "Stratify" or "Principia"
    tool: str  # Tool name
    parameters: Dict[str, Any]
    priority: str = "normal"  # normal, high, low
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "request_id": self.request_id,
            "requester": self.requester,
            "tool": self.tool,
            "parameters": self.parameters,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ToolResponse:
    """Response from tool execution."""
    request_id: str
    status: str  # queued, running, completed, failed
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "request_id": self.request_id,
            "status": self.status,
            "results": self.results,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat()
        }


class BaseTool:
    """Base class for all tools."""
    
    def __init__(self, name: str):
        self.name = name
        self.last_execution_time = 0.0
        self.execution_count = 0
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        start_time = time.time()
        
        try:
            results = self._execute_impl(parameters)
            self.last_execution_time = time.time() - start_time
            self.execution_count += 1
            return results
        except Exception as e:
            self.last_execution_time = time.time() - start_time
            raise e
    
    def _execute_impl(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation-specific execution. Override in subclasses."""
        raise NotImplementedError


class LatticeQCDTool(BaseTool):
    """Lattice QCD simulation tool."""
    
    def __init__(self):
        super().__init__("lattice_qcd")
        # Import lattice module
        import sys
        sys.path.insert(0, '/home/ubuntu/aether/tools')
        from lattice_qcd import run_lattice_simulation
        self.run_simulation = run_lattice_simulation
    
    def _execute_impl(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run lattice QCD simulation."""
        # Run actual lattice simulation
        results = self.run_simulation(parameters)
        return results


class VisualizationTool(BaseTool):
    """Generate diagrams and visualizations."""
    
    def __init__(self):
        super().__init__("visualization")
    
    def _execute_impl(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization."""
        viz_type = parameters.get("type", "generic")
        
        return {
            "type": viz_type,
            "image_path": None,  # Will be populated when implemented
            "description": f"Generated {viz_type} visualization",
            "note": "Visualization tool executed"
        }


class ImageAnalysisTool(BaseTool):
    """Analyze images and extract information."""
    
    def __init__(self):
        super().__init__("image_analysis")
    
    def _execute_impl(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image."""
        image_path = parameters.get("image_path")
        question = parameters.get("question", "Describe this image")
        
        return {
            "image_path": image_path,
            "question": question,
            "answer": "Image analysis result",  # Will use actual vision
            "note": "Image analysis tool executed"
        }


class ResearchTool(BaseTool):
    """Web research and paper search."""
    
    def __init__(self):
        super().__init__("research")
    
    def _execute_impl(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct research."""
        query = parameters.get("query")
        sources = parameters.get("sources", ["web"])
        
        return {
            "query": query,
            "sources": sources,
            "findings": [],  # Will be populated with actual search
            "references": [],
            "note": "Research tool executed"
        }


class PaperAnalysisTool(BaseTool):
    """Deep analysis of academic papers."""
    
    def __init__(self):
        super().__init__("paper_analysis")
    
    def _execute_impl(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze paper."""
        paper_id = parameters.get("paper_id")
        focus = parameters.get("focus", "main results")
        
        return {
            "paper_id": paper_id,
            "focus": focus,
            "summary": "Paper analysis summary",  # Will use actual analysis
            "key_equations": [],
            "relevant_sections": [],
            "note": "Paper analysis tool executed"
        }


class ToolManager:
    """
    Manages all computational tools and request queue.
    
    Manus owns this manager and processes requests from frameworks.
    """
    
    def __init__(self):
        self.queue: List[ToolRequest] = []
        self.current_execution: Optional[ToolRequest] = None
        self.results_cache: Dict[str, ToolResponse] = {}
        
        # Initialize available tools
        self.tools: Dict[str, BaseTool] = {
            "lattice_qcd": LatticeQCDTool(),
            "visualization": VisualizationTool(),
            "image_analysis": ImageAnalysisTool(),
            "research": ResearchTool(),
            "paper_analysis": PaperAnalysisTool(),
        }
        
        # Statistics
        self.total_requests = 0
        self.completed_requests = 0
        self.failed_requests = 0
        
        # Request log for reporting
        self.request_log: List[Dict[str, Any]] = []
    
    def submit_request(self, requester: str, tool: str, 
                      parameters: Dict[str, Any], 
                      priority: str = "normal") -> str:
        """
        Submit a tool request.
        
        Returns:
            request_id: Unique identifier for tracking
        """
        request_id = str(uuid.uuid4())[:8]
        
        request = ToolRequest(
            request_id=request_id,
            requester=requester,
            tool=tool,
            parameters=parameters,
            priority=priority
        )
        
        # Add to queue
        if priority == "high":
            self.queue.insert(0, request)
        else:
            self.queue.append(request)
        
        self.total_requests += 1
        
        # Log request
        self.request_log.append({
            "action": "submitted",
            "request": request.to_dict(),
            "queue_position": len(self.queue)
        })
        
        # Create initial response
        response = ToolResponse(
            request_id=request_id,
            status="queued"
        )
        self.results_cache[request_id] = response
        
        return request_id
    
    def get_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of a request."""
        if request_id in self.results_cache:
            return self.results_cache[request_id].to_dict()
        
        return {"status": "not_found"}
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status."""
        return {
            "queue_length": len(self.queue),
            "current_execution": self.current_execution.to_dict() if self.current_execution else None,
            "pending_requests": [req.to_dict() for req in self.queue],
            "total_requests": self.total_requests,
            "completed_requests": self.completed_requests,
            "failed_requests": self.failed_requests
        }
    
    def process_next_request(self) -> Optional[ToolResponse]:
        """
        Process the next request in queue.
        
        Returns:
            ToolResponse if a request was processed, None if queue empty
        """
        if self.current_execution:
            # Still working on previous request
            return None
        
        if not self.queue:
            # Nothing to do
            return None
        
        # Get next request
        request = self.queue.pop(0)
        self.current_execution = request
        
        # Update status
        response = self.results_cache[request.request_id]
        response.status = "running"
        
        # Log execution start
        self.request_log.append({
            "action": "started",
            "request_id": request.request_id,
            "tool": request.tool,
            "requester": request.requester
        })
        
        try:
            # Execute tool
            if request.tool not in self.tools:
                raise ValueError(f"Unknown tool: {request.tool}")
            
            tool = self.tools[request.tool]
            results = tool.execute(request.parameters)
            
            # Update response
            response.status = "completed"
            response.results = results
            response.execution_time = tool.last_execution_time
            response.timestamp = datetime.now()
            
            self.completed_requests += 1
            
            # Log completion
            self.request_log.append({
                "action": "completed",
                "request_id": request.request_id,
                "execution_time": tool.last_execution_time,
                "results_summary": str(results)[:200]
            })
            
        except Exception as e:
            # Handle error
            response.status = "failed"
            response.error = str(e)
            response.timestamp = datetime.now()
            
            self.failed_requests += 1
            
            # Log failure
            self.request_log.append({
                "action": "failed",
                "request_id": request.request_id,
                "error": str(e)
            })
        
        finally:
            self.current_execution = None
        
        return response
    
    def process_all_pending(self) -> List[ToolResponse]:
        """Process all pending requests in queue."""
        responses = []
        
        while self.queue:
            response = self.process_next_request()
            if response:
                responses.append(response)
        
        return responses
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about tool usage."""
        tool_stats = {}
        
        for tool_name, tool in self.tools.items():
            tool_stats[tool_name] = {
                "execution_count": tool.execution_count,
                "last_execution_time": tool.last_execution_time
            }
        
        return {
            "total_requests": self.total_requests,
            "completed_requests": self.completed_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.completed_requests / self.total_requests if self.total_requests > 0 else 0,
            "tool_usage": tool_stats
        }
    
    def get_request_log(self) -> List[Dict[str, Any]]:
        """Get full request log for reporting."""
        return self.request_log
    
    def clear_old_results(self, max_age_hours: int = 24):
        """Clear old results from cache."""
        current_time = datetime.now()
        to_remove = []
        
        for request_id, response in self.results_cache.items():
            age = (current_time - response.timestamp).total_seconds() / 3600
            if age > max_age_hours and response.status in ["completed", "failed"]:
                to_remove.append(request_id)
        
        for request_id in to_remove:
            del self.results_cache[request_id]
        
        return len(to_remove)


# Singleton instance for Manus to use
_tool_manager_instance = None

def get_tool_manager() -> ToolManager:
    """Get the global tool manager instance."""
    global _tool_manager_instance
    if _tool_manager_instance is None:
        _tool_manager_instance = ToolManager()
    return _tool_manager_instance
