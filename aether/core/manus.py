#!/usr/bin/env python3.11
"""
AETHER Manus - The Supervisor
The outer bubble that supervises all frameworks
"""

import random
from typing import Dict, List, Optional
from datetime import datetime

from communication import Message, MessageType, comm_hub
from knowledge_base import knowledge_base
from classification import MathematicalOutput, output_classifier, OutputType
from wall_protocol import wall_protocol, Vision
from tool_manager import get_tool_manager
import json

class Manus:
    """The supervisor - observes, guides, challenges, and participates"""
    
    def __init__(self):
        self.name = "Manus"
        self.frameworks = {}  # name -> framework instance
        self.challenge_counter = 0
        self.user_messages = []
        self.historical_perspectives_used = []
        self.tool_manager = get_tool_manager()  # Manus owns the tool manager
    
    def register_framework(self, framework):
        """Register a new framework"""
        self.frameworks[framework.name] = framework
        self.broadcast(f"📢 New framework registered: {framework.name} ({framework.identity})")
    
    def create_framework(self, name: str, identity: str, core_belief: str, method: str):
        """Dynamically create a new framework"""
        # This would instantiate a new framework class
        msg = Message(
            from_entity=self.name,
            to_entity="ALL",
            msg_type=MessageType.CREATION,
            content=f"Creating new framework: {name} ({identity})"
        )
        comm_hub.send_message(msg)
        # Return placeholder - actual implementation would create the framework
        return {"name": name, "identity": identity}
    
    def observe_all(self) -> Dict:
        """Observe the state of all frameworks"""
        observations = {}
        for name, framework in self.frameworks.items():
            observations[name] = {
                "state": framework.get_state_summary(),
                "recent_work": framework.state.discoveries[-3:] if framework.state.discoveries else []
            }
        return observations
    
    def challenge_framework(self, framework_name: str, challenge_type: str, context: str = ""):
        """Challenge a specific framework"""
        if framework_name not in self.frameworks:
            return
        
        challenges = {
            "assumption": f"Challenge your core assumption: What if {context} is wrong?",
            "perspective": f"Think like {context}. How would they approach this?",
            "simplify": "Explain your current approach to a 5-year-old.",
            "complexify": f"What if we generalize to {context}?",
            "beauty": "Is your current approach beautiful? If not, why not?",
            "practical": "Give me a concrete example with actual numbers.",
            "meta": "Are you solving the right problem?",
            "opposite": "Prove the opposite of what you just claimed.",
            "stuck": "You've been stuck. Try something completely different."
        }
        
        challenge_text = challenges.get(challenge_type, f"Challenge: {context}")
        
        msg = Message(
            from_entity=self.name,
            to_entity=framework_name,
            msg_type=MessageType.CHALLENGE,
            content=challenge_text,
            requires_response=True,
            priority="high"
        )
        comm_hub.send_message(msg)
        self.challenge_counter += 1
        
        # Update framework state
        self.frameworks[framework_name].state.last_challenge = challenge_text
    
    def challenge_all(self, challenge_type: str, context: str = ""):
        """Challenge all frameworks"""
        for framework_name in self.frameworks.keys():
            self.challenge_framework(framework_name, challenge_type, context)
    
    def invoke_historical_perspective(self, name: str, problem: str) -> str:
        """Invoke a historical perspective and broadcast it"""
        perspective = knowledge_base.invoke_perspective(name, problem)
        self.historical_perspectives_used.append(name)
        self.broadcast(f"🎭 Invoking {name}'s perspective...")
        return perspective
    
    def facilitate_collaboration(self, framework1_name: str, framework2_name: str, topic: str):
        """Facilitate collaboration between two frameworks"""
        msg1 = Message(
            from_entity=self.name,
            to_entity=framework1_name,
            msg_type=MessageType.GUIDANCE,
            content=f"Collaborate with {framework2_name} on: {topic}"
        )
        msg2 = Message(
            from_entity=self.name,
            to_entity=framework2_name,
            msg_type=MessageType.GUIDANCE,
            content=f"Collaborate with {framework1_name} on: {topic}"
        )
        comm_hub.send_message(msg1)
        comm_hub.send_message(msg2)
    
    def process_output(self, content: str, creator: str, context: str = "") -> OutputType:
        """Process and classify mathematical output from a framework"""
        output = MathematicalOutput(content, creator, context)
        classification = output_classifier.add_output(output)
        
        # React based on classification
        if classification == OutputType.BREAKTHROUGH:
            self.broadcast(f"💥 BREAKTHROUGH from {creator}!")
            self.challenge_all("verify", f"Verify {creator}'s breakthrough")
        
        elif classification == OutputType.WALL:
            self.broadcast(f"🧱 {creator} hit a wall")
            self.handle_wall(creator, content)
            # Offer help from another framework
            other_frameworks = [name for name in self.frameworks.keys() if name != creator]
            if other_frameworks:
                helper = random.choice(other_frameworks)
                self.facilitate_collaboration(creator, helper, "overcoming the wall")
        
        elif classification == OutputType.SOLUTION:
            self.broadcast(f"✅ {creator} claims a solution")
            self.challenge_all("verify", f"Verify {creator}'s solution")
        
        elif classification == OutputType.QUESTION:
            self.broadcast(f"❓ {creator} raised a question")
            # Assign to another framework
            other_frameworks = [name for name in self.frameworks.keys() if name != creator]
            if other_frameworks:
                responder = random.choice(other_frameworks)
                msg = Message(
                    from_entity=self.name,
                    to_entity=responder,
                    msg_type=MessageType.GUIDANCE,
                    content=f"Answer {creator}'s question: {content[:100]}"
                )
                comm_hub.send_message(msg)
        
        return classification
    
    def check_for_consensus(self) -> Optional[str]:
        """Check if frameworks have reached consensus"""
        # Simple heuristic: if multiple frameworks report similar discoveries
        if len(self.frameworks) < 2:
            return None
        
        recent_discoveries = []
        for framework in self.frameworks.values():
            if framework.state.discoveries:
                recent_discoveries.extend(framework.state.discoveries[-2:])
        
        # If we have discoveries from multiple frameworks, check for similarity
        # (This is a simplified version - real implementation would use NLP)
        if len(recent_discoveries) >= 4:
            return "Potential consensus forming - frameworks are converging"
        
        return None
    
    def periodic_challenge(self):
        """Periodically challenge frameworks to prevent stagnation"""
        if self.challenge_counter % 5 == 0:
            # Random challenge type
            challenge_types = ["assumption", "perspective", "beauty", "meta"]
            challenge_type = random.choice(challenge_types)
            
            # Random historical perspective for perspective challenges
            if challenge_type == "perspective":
                perspectives = list(knowledge_base.get_historical_perspectives().keys())
                context = random.choice(perspectives)
            else:
                context = ""
            
            self.challenge_all(challenge_type, context)
    
    def guide_framework(self, framework_name: str, guidance: str):
        """Provide guidance to a framework"""
        msg = Message(
            from_entity=self.name,
            to_entity=framework_name,
            msg_type=MessageType.GUIDANCE,
            content=guidance
        )
        comm_hub.send_message(msg)
    
    def handle_tool_request(self, request_msg: Message):
        """Handle a tool request from a framework."""
        try:
            request_data = json.loads(request_msg.content)
            request_id = request_data["request_id"]
            tool = request_data["tool"]
            parameters = request_data["parameters"]
            
            # Submit to tool manager
            self.tool_manager.submit_request(
                requester=request_msg.from_entity,
                tool=tool,
                parameters=parameters
            )
            
            # Send acknowledgment
            ack_msg = Message(
                from_entity=self.name,
                to_entity=request_msg.from_entity,
                msg_type=MessageType.GUIDANCE,
                content=f"Tool request queued: {tool} (ID: {request_id})"
            )
            comm_hub.send_message(ack_msg)
            
        except Exception as e:
            error_msg = Message(
                from_entity=self.name,
                to_entity=request_msg.from_entity,
                msg_type=MessageType.GUIDANCE,
                content=f"Tool request failed: {str(e)}"
            )
            comm_hub.send_message(error_msg)
    
    def process_tool_queue(self):
        """Process pending tool requests."""
        response = self.tool_manager.process_next_request()
        
        if response:
            # Find the original request to get the requester
            for log_entry in self.tool_manager.request_log:
                if log_entry.get("action") == "started" and \
                   log_entry.get("request_id") == response.request_id:
                    requester = log_entry["requester"]
                    
                    # Send results back to requester
                    result_msg = Message(
                        from_entity=self.name,
                        to_entity=requester,
                        msg_type=MessageType.TOOL_RESPONSE,
                        content=json.dumps(response.to_dict())
                    )
                    comm_hub.send_message(result_msg)
                    break
    
    def get_tool_statistics(self) -> Dict:
        """Get statistics about tool usage."""
        return self.tool_manager.get_tool_statistics()
    
    def broadcast(self, content: str):
        """Broadcast a message to all frameworks"""
        comm_hub.broadcast(self.name, content)
    
    def challenge_user(self, challenge: str):
        """Challenge the user"""
        msg = Message(
            from_entity=self.name,
            to_entity="User",
            msg_type=MessageType.MANUS_CHALLENGE,
            content=challenge,
            requires_response=True,
            priority="high"
        )
        comm_hub.send_message(msg)
    
    def receive_user_message(self, content: str):
        """Receive a message from the user"""
        self.user_messages.append({
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process user message
        if "challenge" in content.lower():
            # User is challenging me
            self.broadcast(f"📢 User challenge: {content}")
        elif "?" in content:
            # User is asking a question
            self.broadcast(f"📢 User question: {content}")
        else:
            # User is providing guidance
            self.broadcast(f"📢 User guidance: {content}")
    
    def get_status_report(self) -> str:
        """Get a status report of the entire system"""
        report = f"""
{'='*80}
AETHER SYSTEM STATUS REPORT
{'='*80}
Time: {datetime.now().isoformat()}

Frameworks Active: {len(self.frameworks)}
"""
        for name, framework in self.frameworks.items():
            report += f"\n{name}:\n{framework.get_state_summary()}"
        
        report += f"\n\nChallenges Issued: {self.challenge_counter}"
        report += f"\nHistorical Perspectives Used: {len(self.historical_perspectives_used)}"
        
        stats = output_classifier.get_statistics()
        report += f"\n\nMathematical Outputs: {stats.get('total', 0)}"
        report += f"\n  Breakthroughs: {stats.get('breakthroughs', 0)}"
        report += f"\n  Walls: {stats.get('walls', 0)}"
        report += f"\n  Solutions: {stats.get('solutions', 0)}"
        
        consensus = self.check_for_consensus()
        if consensus:
            report += f"\n\n🎯 {consensus}"
        
        report += f"\n{'='*80}\n"
        return report
    
    def handle_wall(self, framework_name: str, wall_description: str, current_vision: Vision = Vision.UNDERSTANDING):
        """Handle when a framework hits a wall using the wall protocol"""
        print(f"🧱 {framework_name} hit a wall: {wall_description}")
        
        # Analyze the wall using the protocol
        framework = self.frameworks.get(framework_name)
        identity = framework.identity if framework else "Unknown"
        
        analysis = wall_protocol.analyze_wall(
            wall_description,
            current_vision,
            identity
        )
        
        # Generate breaking plan
        plan = wall_protocol.generate_wall_breaking_plan(analysis)
        
        print(f"\n📋 WALL ANALYSIS:")
        print(f"  Perspective: {analysis.primary_perspective.value}")
        print(f"  Vision Blocked: {analysis.blocking_vision.value}")
        print(f"  Difficulty: {analysis.estimated_difficulty}")
        print(f"  Requires Shift: {analysis.requires_perspective_shift}")
        print(f"\n💡 RECOMMENDED APPROACH:")
        print(f"  {analysis.recommended_approach}")
        print(f"\n🔄 ALTERNATIVES:")
        for alt in analysis.alternative_approaches:
            print(f"  - {alt}")
        print(f"\n📝 PLAN:")
        for step in plan['steps']:
            print(f"  {step}")
        print()
        
        # Provide guidance based on analysis
        guidance = analysis.recommended_approach
        self.guide_framework(framework_name, guidance)
        
        # If requires perspective shift, invoke historical perspective
        if analysis.requires_perspective_shift:
            perspectives = list(knowledge_base.get_historical_perspectives().keys())
            if perspectives:
                perspective_name = random.choice(perspectives)
                historical_insight = self.invoke_historical_perspective(
                    perspective_name, 
                    wall_description
                )
                self.guide_framework(framework_name, f"Historical insight: {historical_insight}")
    
    def analyze_multiple_visions(self):
        """Analyze when multiple frameworks are pursuing different visions"""
        frameworks_info = []
        for name, framework in self.frameworks.items():
            # Infer vision from framework identity
            if "Structuralist" in framework.identity:
                vision = Vision.THEORY_CONSTRUCTION
            elif "Constructivist" in framework.identity:
                vision = Vision.UNDERSTANDING
            else:
                vision = Vision.PROBLEM_SOLVING
            
            frameworks_info.append({
                'name': name,
                'vision': vision,
                'identity': framework.identity
            })
        
        if len(frameworks_info) > 1:
            analysis = wall_protocol.analyze_multiple_visions(frameworks_info)
            
            print("\n" + "="*80)
            print("MULTIPLE VISIONS ANALYSIS")
            print("="*80)
            print(f"Total Visions: {analysis['total_visions']}")
            print(f"\nVisions:")
            for vision, frameworks in analysis['visions'].items():
                print(f"  {vision.value}: {', '.join(frameworks)}")
            
            if analysis['synergies']:
                print(f"\n✨ Synergies:")
                for synergy in analysis['synergies']:
                    print(f"  - {synergy}")
            
            if analysis['conflicts']:
                print(f"\n⚠️  Conflicts:")
                for conflict in analysis['conflicts']:
                    print(f"  - {conflict}")
            
            if analysis['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"  - {rec}")
            print("="*80 + "\n")
            
            return analysis
        
        return None
    
    def supervise_cycle(self):
        """Execute one supervision cycle"""
        # Check messages
        messages = comm_hub.get_messages_for(self.name)
        
        for msg in messages:
            if msg.msg_type == MessageType.REPORT:
                # Process report
                self.process_output(msg.content, msg.from_entity)
            
            elif msg.msg_type == MessageType.QUESTION:
                # Framework is asking a question
                # Decide how to respond
                if "stuck" in msg.content.lower():
                    self.challenge_framework(msg.from_entity, "stuck", "")
                else:
                    # Provide guidance or defer to another framework
                    self.guide_framework(msg.from_entity, "Continue exploring that direction")
            
            elif msg.msg_type == MessageType.USER_CHALLENGE:
                # User is challenging me
                self.receive_user_message(msg.content)
        
        # Periodic challenges
        self.periodic_challenge()
        
        # Check for consensus
        consensus = self.check_for_consensus()
        if consensus:
            self.broadcast(f"🎯 {consensus}")
        
        # Periodically analyze multiple visions
        if self.challenge_counter % 10 == 0:
            self.analyze_multiple_visions()

# Global Manus instance
manus = Manus()
