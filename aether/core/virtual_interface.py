"""
Virtual Interface Layer for AETHER

This layer makes shared tools appear local to frameworks through
transparent proxies. Frameworks can't tell the difference between
local and shared tools.

The "Hotel Suite Model":
- Small rooms for AIs (lightweight workspaces)
- Big shared center (heavy tools and mathematics)
- Virtual interfaces (seamless access)
"""

import inspect
from typing import Any, Dict, Callable
from datetime import datetime


class VirtualTool:
    """
    A virtual tool that appears local but is actually shared.
    
    The framework thinks it's calling a local method, but the call
    is transparently routed to the shared center.
    
    Example:
        # Framework code (looks local):
        result = self.lattice.run_simulation(beta=6.0)
        
        # Reality: Routed to shared center's lattice tool
        # Framework can't tell the difference!
    """
    
    def __init__(self, tool_name: str, shared_center: 'SharedCenter'):
        self._tool_name = tool_name
        self._shared_center = shared_center
        self._call_history = []
    
    def __getattr__(self, method_name: str):
        """
        Intercept any method call and route to shared center.
        This is the magic that makes it feel local!
        """
        if method_name.startswith('_'):
            # Private attributes - don't intercept
            raise AttributeError(f"'{self._tool_name}' has no attribute '{method_name}'")
        
        def virtual_method(*args, **kwargs):
            # Log the call
            call_info = {
                'tool': self._tool_name,
                'method': method_name,
                'timestamp': datetime.now(),
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
            self._call_history.append(call_info)
            
            # Route to shared center
            result = self._shared_center.execute_tool(
                tool_name=self._tool_name,
                method_name=method_name,
                args=args,
                kwargs=kwargs
            )
            
            return result
        
        return virtual_method
    
    def __repr__(self):
        return f"<VirtualTool: {self._tool_name}>"


class VirtualInterfaceLayer:
    """
    Creates and manages virtual interfaces for frameworks.
    
    Each framework gets a set of virtual tools that appear local
    but are actually shared.
    """
    
    def __init__(self, shared_center: 'SharedCenter'):
        self.shared_center = shared_center
        self.active_interfaces: Dict[str, Dict[str, VirtualTool]] = {}
        self.access_log = []
    
    def create_interface_for(self, framework_name: str) -> Dict[str, VirtualTool]:
        """
        Create a complete set of virtual tools for a framework.
        
        Returns:
            Dictionary mapping tool names to VirtualTool instances
        """
        # Get available tools from shared center
        available_tools = self.shared_center.get_available_tools()
        
        # Create virtual interface for each tool
        interface = {}
        for tool_name in available_tools:
            interface[tool_name] = VirtualTool(tool_name, self.shared_center)
        
        # Store the interface
        self.active_interfaces[framework_name] = interface
        
        # Log creation
        self.access_log.append({
            'action': 'interface_created',
            'framework': framework_name,
            'tools': list(available_tools),
            'timestamp': datetime.now()
        })
        
        return interface
    
    def get_interface_for(self, framework_name: str) -> Dict[str, VirtualTool]:
        """Get the virtual interface for a framework."""
        if framework_name not in self.active_interfaces:
            return self.create_interface_for(framework_name)
        return self.active_interfaces[framework_name]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics across all interfaces."""
        stats = {
            'total_frameworks': len(self.active_interfaces),
            'total_tools': len(self.shared_center.get_available_tools()),
            'framework_stats': {}
        }
        
        for framework_name, interface in self.active_interfaces.items():
            total_calls = 0
            tool_usage = {}
            
            for tool_name, virtual_tool in interface.items():
                calls = len(virtual_tool._call_history)
                total_calls += calls
                if calls > 0:
                    tool_usage[tool_name] = calls
            
            stats['framework_stats'][framework_name] = {
                'total_calls': total_calls,
                'tools_used': len(tool_usage),
                'tool_usage': tool_usage
            }
        
        return stats


class SharedCenter:
    """
    The big room where actual tools live.
    
    Only one instance of each tool exists here.
    All frameworks access them through virtual interfaces.
    """
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.execution_log = []
        self.shared_storage = {}
    
    def register_tool(self, name: str, tool_instance: Any):
        """Register a tool in the shared center."""
        self.tools[name] = tool_instance
        print(f"✓ Registered tool: {name}")
    
    def get_available_tools(self) -> list:
        """Get list of available tool names."""
        return list(self.tools.keys())
    
    def execute_tool(self, tool_name: str, method_name: str, 
                     args: tuple, kwargs: dict) -> Any:
        """
        Execute a method on a shared tool.
        
        This is called by VirtualTool instances when frameworks
        make method calls.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in shared center")
        
        tool = self.tools[tool_name]
        
        if not hasattr(tool, method_name):
            raise AttributeError(f"Tool '{tool_name}' has no method '{method_name}'")
        
        method = getattr(tool, method_name)
        
        # Log execution
        log_entry = {
            'tool': tool_name,
            'method': method_name,
            'timestamp': datetime.now(),
            'args_count': len(args),
            'kwargs_count': len(kwargs)
        }
        
        try:
            # Execute the actual method
            result = method(*args, **kwargs)
            log_entry['status'] = 'success'
            self.execution_log.append(log_entry)
            return result
        
        except Exception as e:
            log_entry['status'] = 'failed'
            log_entry['error'] = str(e)
            self.execution_log.append(log_entry)
            raise
    
    def store_result(self, key: str, value: Any):
        """Store a result in shared storage."""
        self.shared_storage[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    def get_result(self, key: str) -> Any:
        """Retrieve a result from shared storage."""
        if key in self.shared_storage:
            return self.shared_storage[key]['value']
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total_executions = len(self.execution_log)
        successful = sum(1 for log in self.execution_log if log['status'] == 'success')
        failed = total_executions - successful
        
        tool_usage = {}
        for log in self.execution_log:
            tool = log['tool']
            if tool not in tool_usage:
                tool_usage[tool] = 0
            tool_usage[tool] += 1
        
        return {
            'total_executions': total_executions,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total_executions if total_executions > 0 else 0,
            'tool_usage': tool_usage,
            'storage_items': len(self.shared_storage)
        }


class InteractiveWorkspace:
    """
    A virtual workspace that feels unlimited.
    
    Provides frameworks with an "infinite" workspace through
    clever interfaces to shared tools.
    """
    
    def __init__(self, framework_name: str, virtual_interface: Dict[str, VirtualTool]):
        self.framework_name = framework_name
        self.virtual_interface = virtual_interface
        
        # Virtual components (all backed by shared tools)
        self.canvas = self._create_virtual_canvas()
        self.lab = self._create_virtual_lab()
        self.library = self._create_virtual_library()
    
    def _create_virtual_canvas(self):
        """Virtual canvas for visualizations."""
        class VirtualCanvas:
            def __init__(self, visualizer):
                self.visualizer = visualizer
            
            def render(self, concept):
                """Render a mathematical concept."""
                if hasattr(self.visualizer, 'render'):
                    return self.visualizer.render(concept)
                return f"Rendered: {concept}"
            
            def draw(self, *args, **kwargs):
                """Draw on the canvas."""
                if hasattr(self.visualizer, 'draw'):
                    return self.visualizer.draw(*args, **kwargs)
                return "Drawing created"
        
        visualizer = self.virtual_interface.get('visualizer')
        return VirtualCanvas(visualizer) if visualizer else None
    
    def _create_virtual_lab(self):
        """Virtual lab for experiments."""
        class VirtualLab:
            def __init__(self, tools):
                self.tools = tools
            
            def run_experiment(self, experiment):
                """Run an experiment."""
                # Route to appropriate tool
                return f"Experiment '{experiment}' executed"
        
        return VirtualLab(self.virtual_interface)
    
    def _create_virtual_library(self):
        """Virtual library for research."""
        class VirtualLibrary:
            def __init__(self, researcher):
                self.researcher = researcher
            
            def search(self, query):
                """Search for papers/theorems."""
                if hasattr(self.researcher, 'search'):
                    return self.researcher.search(query)
                return f"Search results for: {query}"
            
            def get_theorem(self, name):
                """Get a specific theorem."""
                if hasattr(self.researcher, 'get_theorem'):
                    return self.researcher.get_theorem(name)
                return f"Theorem: {name}"
        
        researcher = self.virtual_interface.get('researcher')
        return VirtualLibrary(researcher) if researcher else None


# Global shared center instance
_shared_center = None
_virtual_interface_layer = None

def get_shared_center() -> SharedCenter:
    """Get the global shared center instance."""
    global _shared_center
    if _shared_center is None:
        _shared_center = SharedCenter()
    return _shared_center

def get_virtual_interface_layer() -> VirtualInterfaceLayer:
    """Get the global virtual interface layer instance."""
    global _virtual_interface_layer
    if _virtual_interface_layer is None:
        _virtual_interface_layer = VirtualInterfaceLayer(get_shared_center())
    return _virtual_interface_layer
